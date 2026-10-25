using System.Net;
using Microsoft.AspNetCore.Html;
using Umbraco.Cms.Core.Models;
using Umbraco.Cms.Core.Models.Blocks;
using Umbraco.Cms.Core.Models.PublishedContent;
using Umbraco.Extensions;

namespace BroudoHoldings.Helpers;

/// <summary>Small helpers shared by the block partials in Views/Partials/Blocks.</summary>
public static class BlockHelpers
{
    /// <summary>A text property, or null when it is empty.</summary>
    public static string? Text(this IPublishedElement element, string alias)
    {
        var value = element.Value<string>(alias);
        return string.IsNullOrWhiteSpace(value) ? null : value.Trim();
    }

    /// <summary>The element items of a nested Block List property.</summary>
    public static List<IPublishedElement> Items(this IPublishedElement element, string alias)
        => element.Value<BlockListModel>(alias)?.Select(item => item.Content).ToList() ?? [];

    public static IPublishedContent? Media(this IPublishedElement element, string alias)
        => element.Value<IPublishedContent>(alias);

    public static List<IPublishedContent> MediaList(this IPublishedElement element, string alias)
        => element.Value<IEnumerable<IPublishedContent>>(alias)?.ToList() ?? [];

    public static Link? FirstLink(this IPublishedElement element, string alias)
        => element.Value<IEnumerable<Link>>(alias)?.FirstOrDefault();

    /// <summary>Lines of a multi-line text, without empty lines.</summary>
    public static List<string> Lines(this IPublishedElement element, string alias)
        => (element.Value<string>(alias) ?? "")
            .Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .ToList();

    /// <summary>Renders a multi-line text as paragraphs with the given class.</summary>
    public static IHtmlContent Paragraphs(string? text, string cssClass)
    {
        if (string.IsNullOrWhiteSpace(text))
        {
            return HtmlString.Empty;
        }

        var paragraphs = text.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .Select(line => $"<p class=\"{cssClass}\">{WebUtility.HtmlEncode(line)}</p>");
        return new HtmlString(string.Join("\n", paragraphs));
    }

    /// <summary>
    /// A photo in the prototype's frame: the image when one is picked, otherwise the grey placeholder box
    /// with its label (class "ph"). <paramref name="inner"/> is rendered on top (e.g. the tags of a project card).
    /// </summary>
    public static IHtmlContent Photo(IPublishedContent? media, string cssClass, string? label, string? alt = null, IHtmlContent? inner = null)
    {
        var html = new HtmlContentBuilder();
        html.AppendHtml($"<div class=\"ph {cssClass}\">");
        if (media?.Url() is { Length: > 0 } src)
        {
            html.AppendHtml($"<img class=\"ph__img\" src=\"{WebUtility.HtmlEncode(src)}\" alt=\"{WebUtility.HtmlEncode(alt ?? "")}\" loading=\"lazy\">");
        }
        else
        {
            html.Append(label ?? "");
        }

        if (inner is not null)
        {
            html.AppendHtml(inner);
        }

        html.AppendHtml("</div>");
        return html;
    }
}

/// <summary>Model for Views/Partials/Blocks/_Buttons.cshtml.</summary>
public record ButtonGroup(IReadOnlyList<IPublishedElement> Buttons);

/// <summary>Model for Views/Partials/Broudo/CallToAction.cshtml.</summary>
public record CallToAction(string Heading, string? Subtitle = null, IReadOnlyList<IPublishedElement>? Buttons = null);
