using Umbraco.Cms.Core.Composing;
using Umbraco.Cms.Core.DependencyInjection;
using Umbraco.Cms.Core.Events;
using Umbraco.Cms.Core.Models;
using Umbraco.Cms.Core.Notifications;
using Umbraco.Cms.Core.Services;

namespace BroudoHoldings.Seeding;

/// <summary>
/// Development, or when Broudo:SeedDefaultContent is on (the server's first start). Creates the empty page tree
/// (Home + section pages) on a fresh database, so every Razor template has a URL to render at, then fills empty
/// pages with the default content (see <see cref="DefaultContentSeeder"/>). Never changes content that editors created.
/// </summary>
public class DevelopmentContentSeeder : INotificationAsyncHandler<UmbracoApplicationStartedNotification>
{
    private static readonly (string Name, string Alias)[] SectionPages =
    [
        ("About", "AboutPage"),
        ("Projects", "ProjectsPage"),
        ("Markets", "MarketsPage"),
        ("Contact", "ContactPage"),
    ];

    private readonly IHostEnvironment _environment;
    private readonly IConfiguration _configuration;
    private readonly IContentService _contentService;
    private readonly IContentTypeService _contentTypeService;
    private readonly ITemplateService _templateService;
    private readonly ILanguageService _languageService;
    private readonly DefaultContentSeeder _defaultContent;
    private readonly ILogger<DevelopmentContentSeeder> _logger;

    public DevelopmentContentSeeder(
        IHostEnvironment environment,
        IConfiguration configuration,
        IContentService contentService,
        IContentTypeService contentTypeService,
        ITemplateService templateService,
        ILanguageService languageService,
        DefaultContentSeeder defaultContent,
        ILogger<DevelopmentContentSeeder> logger)
    {
        _environment = environment;
        _configuration = configuration;
        _contentService = contentService;
        _contentTypeService = contentTypeService;
        _templateService = templateService;
        _languageService = languageService;
        _defaultContent = defaultContent;
        _logger = logger;
    }

    public async Task HandleAsync(UmbracoApplicationStartedNotification notification, CancellationToken cancellationToken)
    {
        if (!_environment.IsDevelopment() && !_configuration.GetValue<bool>("Broudo:SeedDefaultContent"))
        {
            return;
        }

        if (_contentTypeService.Get("HomePage") is null || await _templateService.GetAsync("HomePage") is null)
        {
            _logger.LogWarning("Broudo Holdings seeding skipped: document types or templates were not imported yet. Restart after uSync import.");
            return;
        }

        var culture = await _languageService.GetDefaultIsoCodeAsync();
        var home = _contentService.GetRootContent().FirstOrDefault(item => item.ContentType.Alias == "HomePage");
        if (home is null)
        {
            home = await CreatePageAsync("Home", "HomePage", Umbraco.Cms.Core.Constants.System.Root, culture);
            foreach (var (name, alias) in SectionPages)
            {
                await CreatePageAsync(name, alias, home.Id, culture);
            }

            _logger.LogInformation("Broudo Holdings seeding created {Count} pages.", SectionPages.Length + 1);
        }

        try
        {
            await _defaultContent.SeedAsync(home);
        }
        catch (Exception exception)
        {
            // Never stop the site from starting because of the default content
            _logger.LogError(exception, "Broudo Holdings seeding could not load the default content.");
        }
    }

    private async Task<IContent> CreatePageAsync(string name, string alias, int parentId, string culture)
    {
        var content = _contentService.Create(name, parentId, alias);
        content.SetCultureName(name, culture);
        content.TemplateId = (await _templateService.GetAsync(alias))?.Id;
        _contentService.Save(content);
        _contentService.Publish(content, [culture]);
        return content;
    }
}

public class DevelopmentContentSeederComposer : IComposer
{
    public void Compose(IUmbracoBuilder builder)
    {
        builder.Services.AddTransient<DefaultContentSeeder>();
        builder.AddNotificationAsyncHandler<UmbracoApplicationStartedNotification, DevelopmentContentSeeder>();
    }
}
