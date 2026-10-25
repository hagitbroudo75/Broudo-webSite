using System.Text.Json;
using System.Text.Json.Nodes;
using Umbraco.Cms.Core;
using Umbraco.Cms.Core.Models;
using Umbraco.Cms.Core.Models.ContentEditing;
using Umbraco.Cms.Core.Services;

namespace BroudoHoldings.Seeding;

/// <summary>
/// Development only. Loads the prototype's default content (Seeding/DefaultContent.json) into Umbraco:
/// site settings, the documents under the section pages (markets, projects, legal pages) and the content blocks of each page.
/// Only empty languages are filled: a page gets the blocks of a language it has no blocks in yet, and a document
/// gets the languages it doesn't have yet. Languages that already have content are never changed.
/// Values go through the same editing service as the backoffice, in the backoffice's (editor) format.
/// </summary>
public class DefaultContentSeeder
{
    private const string FileName = "Seeding/DefaultContent.json";
    private static readonly Guid UserKey = Constants.Security.SuperUserKey;

    private readonly IHostEnvironment _environment;
    private readonly IContentService _contentService;
    private readonly IContentEditingService _contentEditingService;
    private readonly IContentTypeService _contentTypeService;
    private readonly ITemplateService _templateService;
    private readonly ILanguageService _languageService;
    private readonly ILogger<DefaultContentSeeder> _logger;

    /// <summary>Documents that the content refers to: "page:Alias" for section pages, "ref:name" for seeded documents.</summary>
    private readonly Dictionary<string, Guid> _refs = new(StringComparer.OrdinalIgnoreCase);
    private string _defaultCulture = "en-US";

    public DefaultContentSeeder(
        IHostEnvironment environment,
        IContentService contentService,
        IContentEditingService contentEditingService,
        IContentTypeService contentTypeService,
        ITemplateService templateService,
        ILanguageService languageService,
        ILogger<DefaultContentSeeder> logger)
    {
        _environment = environment;
        _contentService = contentService;
        _contentEditingService = contentEditingService;
        _contentTypeService = contentTypeService;
        _templateService = templateService;
        _languageService = languageService;
        _logger = logger;
    }

    public async Task SeedAsync(IContent home)
    {
        var path = Path.Combine(_environment.ContentRootPath, FileName);
        if (!System.IO.File.Exists(path))
        {
            return;
        }

        var data = JsonNode.Parse(await System.IO.File.ReadAllTextAsync(path))!.AsObject();
        _defaultCulture = await _languageService.GetDefaultIsoCodeAsync();
        _refs["page:HomePage"] = home.Key;
        foreach (var child in Children(home.Id))
        {
            _refs.TryAdd("page:" + child.ContentType.Alias, child.Key);
        }

        await SeedSiteSettingsAsync(data["settings"]?.AsObject());
        foreach (var group in data["children"]!.AsArray().Select(group => group!.AsObject()))
        {
            await SeedChildrenAsync((string)group["parent"]!, (string)group["type"]!, group["items"]!.AsArray());
        }

        foreach (var (alias, cultures) in data["pages"]!.AsObject())
        {
            await SeedPageAsync(alias, cultures!.AsObject());
        }
    }

    // ── Pages ───────────────────────────────────────────────────────────────

    private async Task SeedPageAsync(string alias, JsonObject blocksByCulture)
    {
        if (!_refs.TryGetValue("page:" + alias, out var key) || _contentService.GetById(key) is not { } page)
        {
            _logger.LogWarning("Default content: page {Alias} not found, skipped.", alias);
            return;
        }

        var newBlocks = blocksByCulture.Where(entry => page.AvailableCultures.Contains(entry.Key) && !HasValue(page, "contentBlocks", entry.Key)).ToList();
        if (newBlocks.Count == 0)
        {
            return;
        }

        var contentType = _contentTypeService.Get(page.ContentType.Key)!;
        var cultures = page.AvailableCultures.ToList();
        var publish = cultures.Where(page.IsCulturePublished).Union(newBlocks.Select(entry => entry.Key)).ToArray();
        var model = new ContentUpdateModel
        {
            TemplateKey = await TemplateKeyAsync(page),
            Variants = cultures.Select(culture => new VariantModel { Culture = culture, Name = page.GetCultureName(culture) ?? page.Name! }).ToList(),
            Properties = newBlocks.Select(entry => Property(contentType, "contentBlocks", entry.Value!, entry.Key)).ToList(),
        };
        var result = await _contentEditingService.UpdateAndPublishAsync(page.Key, model, publish, UserKey);
        Log(result.Success, result.Status, $"page {alias} ({string.Join(", ", newBlocks.Select(entry => entry.Key))})");
    }

    private static bool HasValue(IContent content, string alias, string culture)
        => content.GetValue(alias, culture) is { } value && value.ToString() is { Length: > 0 } text && text != "[]";

    // ── Documents under the section pages, site settings ─────────────────────

    private async Task SeedChildrenAsync(string parentAlias, string childAlias, JsonArray items)
    {
        if (!_refs.TryGetValue("page:" + parentAlias, out var parentKey) || _contentService.GetById(parentKey) is not { } parent)
        {
            _logger.LogWarning("Default content: page {Alias} not found, {Type} skipped.", parentAlias, childAlias);
            return;
        }

        var contentType = _contentTypeService.Get(childAlias)!;
        var existing = Children(parent.Id).Where(child => child.ContentType.Alias == childAlias).ToList();
        var templateKey = (await _templateService.GetAsync(childAlias))?.Key;
        var create = existing.Count == 0;
        foreach (var item in items.Select(item => item!.AsObject()))
        {
            if (create)
            {
                var key = Guid.NewGuid();
                if (await CreateAsync(contentType, parent.Key, templateKey, item, key) && item["ref"] is not null)
                {
                    _refs["ref:" + (string)item["ref"]!] = key;
                }

                continue;
            }

            // Already created: remember them so other content can refer to them (matched by their name in the
            // default language), and add the languages they don't have yet
            var name = (string?)item["names"]?[_defaultCulture];
            if (existing.FirstOrDefault(child => child.GetCultureName(_defaultCulture) == name) is not { } match)
            {
                continue;
            }

            if (item["ref"] is not null)
            {
                _refs["ref:" + (string)item["ref"]!] = match.Key;
            }

            await AddCulturesAsync(match, contentType, item);
        }
    }

    /// <summary>Adds the languages of { names, shared, cultures } that a document doesn't have yet.</summary>
    private async Task AddCulturesAsync(IContent content, IContentType contentType, JsonObject item)
    {
        var names = item["names"]!.AsObject();
        var added = names.Select(name => name.Key).Where(culture => !content.AvailableCultures.Contains(culture)).ToArray();
        if (added.Length == 0)
        {
            return;
        }

        var model = new ContentUpdateModel
        {
            TemplateKey = await TemplateKeyAsync(content),
            Variants = content.AvailableCultures.Select(culture => new VariantModel { Culture = culture, Name = content.GetCultureName(culture)! })
                .Concat(added.Select(culture => new VariantModel { Culture = culture, Name = (string)names[culture]! })).ToList(),
            Properties = PropertiesFor(contentType, item, added),
        };
        var publish = content.AvailableCultures.Where(content.IsCulturePublished).Union(added).ToArray();
        var result = await _contentEditingService.UpdateAndPublishAsync(content.Key, model, publish, UserKey);
        Log(result.Success, result.Status, $"{contentType.Alias} \"{content.Name}\" ({string.Join(", ", added)})");
    }

    private List<PropertyValueModel> PropertiesFor(IContentType contentType, JsonObject item, IEnumerable<string> cultures)
    {
        var properties = new List<PropertyValueModel>();
        foreach (var culture in cultures)
        {
            foreach (var (alias, value) in item["shared"]?.AsObject() ?? new JsonObject())
            {
                properties.Add(Property(contentType, alias, value!, culture));
            }

            foreach (var (alias, value) in item["cultures"]?[culture]?.AsObject() ?? new JsonObject())
            {
                properties.Add(Property(contentType, alias, value!, culture));
            }
        }

        return properties;
    }

    private async Task SeedSiteSettingsAsync(JsonObject? settings)
    {
        if (settings is null || _contentService.GetRootContent().Any(item => item.ContentType.Alias == "SiteSettings"))
        {
            return;
        }

        await CreateAsync(_contentTypeService.Get("SiteSettings")!, null, null, settings, Guid.NewGuid());
    }

    /// <summary>Creates and publishes a document from { names, shared, cultures } in every language it has a name in.</summary>
    private async Task<bool> CreateAsync(IContentType contentType, Guid? parentKey, Guid? templateKey, JsonObject item, Guid key)
    {
        var names = item["names"]!.AsObject();
        var cultures = names.Select(name => name.Key).ToArray();
        var model = new ContentCreateModel
        {
            Key = key,
            ContentTypeKey = contentType.Key,
            ParentKey = parentKey,
            TemplateKey = templateKey,
            Variants = names.Select(name => new VariantModel { Culture = name.Key, Name = (string)name.Value! }).ToList(),
            Properties = PropertiesFor(contentType, item, cultures),
        };
        var result = await _contentEditingService.CreateAndPublishAsync(model, cultures, UserKey);
        Log(result.Success, result.Status, $"{contentType.Alias} \"{names[cultures[0]]}\"");
        return result.Success;
    }

    private async Task<Guid?> TemplateKeyAsync(IContent content)
        => content.TemplateId is { } templateId ? (await _templateService.GetAsync(templateId))?.Key : null;

    // ── Values in the backoffice (editor) format ──────────────────────────────

    private PropertyValueModel Property(IContentTypeComposition contentType, string alias, JsonNode value, string culture)
    {
        var propertyType = PropertyType(contentType, alias);
        var editorValue = EditorValue(propertyType, value, culture);
        return new PropertyValueModel
        {
            Alias = alias,
            Culture = culture,
            // Choice editors read a list of strings, the date editor a string and the true/false editor a bool; the others read the JSON as the backoffice sends it
            Value = editorValue switch
            {
                JsonArray list when propertyType.PropertyEditorAlias is Constants.PropertyEditors.Aliases.DropDownListFlexible
                    => list.Select(item => (string)item!).ToArray(),
                JsonValue text when text.GetValueKind() == JsonValueKind.String => (string)text!,
                JsonValue flag when flag.GetValueKind() is JsonValueKind.True or JsonValueKind.False => (bool)flag,
                _ => JsonSerializer.SerializeToElement(editorValue),
            },
        };
    }

    private static IPropertyType PropertyType(IContentTypeComposition contentType, string alias)
        => contentType.CompositionPropertyTypes.FirstOrDefault(property => property.Alias == alias)
           ?? throw new InvalidOperationException($"{contentType.Alias} has no property '{alias}'.");

    private JsonNode? EditorValue(IPropertyType propertyType, JsonNode value, string culture) => propertyType.PropertyEditorAlias switch
    {
        Constants.PropertyEditors.Aliases.BlockList => BlockList(value.AsArray(), culture),
        Constants.PropertyEditors.Aliases.DropDownListFlexible => value is JsonArray ? value.DeepClone() : new JsonArray((string)value!),
        Constants.PropertyEditors.Aliases.MultiUrlPicker => new JsonArray(Link((string)value!)),
        Constants.PropertyEditors.Aliases.ContentPicker => JsonValue.Create(Reference((string)value!).ToString()),
        Constants.PropertyEditors.Aliases.MultiNodeTreePicker => new JsonArray(Values(value)
            .Select(reference => (JsonNode)new JsonObject { ["type"] = "document", ["unique"] = Reference(reference) }).ToArray()),
        Constants.PropertyEditors.Aliases.RichText => new JsonObject { ["markup"] = (string)value!, ["blocks"] = null },
        Constants.PropertyEditors.Aliases.DateTime => JsonValue.Create(DateTime.Parse((string)value!).ToString("yyyy-MM-dd HH:mm:ss")),
        _ => value.DeepClone(),
    };

    /// <summary>
    /// A Block List value. Pages and blocks both vary by language, so every block value and expose entry carries the
    /// language: Umbraco reads blocks without a language as blocks of the default language only.
    /// </summary>
    private JsonObject BlockList(JsonArray blocks, string culture)
    {
        var layout = new JsonArray();
        var contentData = new JsonArray();
        var expose = new JsonArray();
        foreach (var block in blocks.Select(block => block!.AsObject()))
        {
            var elementType = _contentTypeService.Get((string)block["type"]!)
                              ?? throw new InvalidOperationException($"Unknown block type '{block["type"]}'.");
            var key = Guid.NewGuid();
            var values = new JsonArray();
            foreach (var (alias, value) in block.Where(entry => entry.Key != "type"))
            {
                var propertyType = PropertyType(elementType, alias);
                values.Add(new JsonObject
                {
                    ["alias"] = alias,
                    ["culture"] = culture,
                    ["segment"] = null,
                    ["editorAlias"] = propertyType.PropertyEditorAlias,
                    ["value"] = EditorValue(propertyType, value!, culture),
                });
            }

            contentData.Add(new JsonObject { ["key"] = key, ["contentTypeKey"] = elementType.Key, ["values"] = values });
            layout.Add(new JsonObject { ["contentKey"] = key });
            expose.Add(new JsonObject { ["contentKey"] = key, ["culture"] = culture, ["segment"] = null });
        }

        return new JsonObject
        {
            ["layout"] = new JsonObject { [Constants.PropertyEditors.Aliases.BlockList] = layout },
            ["contentData"] = contentData,
            ["settingsData"] = new JsonArray(),
            ["expose"] = expose,
        };
    }

    /// <summary>"page:ContactPage" or "ref:atlanta" (optionally with "#anchor") links to that document; anything else is an external URL.</summary>
    private JsonObject Link(string value)
    {
        if (!value.StartsWith("page:") && !value.StartsWith("ref:"))
        {
            return new JsonObject { ["type"] = "external", ["url"] = value, ["name"] = null, ["target"] = null };
        }

        var parts = value.Split('#', 2);
        return new JsonObject
        {
            ["type"] = "document",
            ["unique"] = Reference(parts[0]),
            ["queryString"] = parts.Length > 1 ? "#" + parts[1] : null,
            ["name"] = null,
            ["target"] = null,
        };
    }

    private Guid Reference(string value) => _refs.TryGetValue(value, out var key)
        ? key
        : throw new InvalidOperationException($"Unknown reference '{value}'.");

    private static IEnumerable<string> Values(JsonNode value) => value is JsonArray array ? array.Select(item => (string)item!) : [(string)value!];

    // ── Helpers ───────────────────────────────────────────────────────────────

    private IEnumerable<IContent> Children(int parentId)
        => _contentService.GetPagedChildren(parentId, 0, 500, out _, propertyAliases: null, filter: null, ordering: null, loadTemplates: true);

    private void Log(bool success, object status, string what)
    {
        if (success)
        {
            _logger.LogInformation("Default content: created {What}.", what);
        }
        else
        {
            _logger.LogError("Default content: could not save {What}: {Status}.", what, status);
        }
    }
}
