using System.Globalization;
using Umbraco.Cms.Core.Models;
using Umbraco.Cms.Core.Models.Blocks;
using Umbraco.Cms.Core.Models.PublishedContent;
using Umbraco.Cms.Web.Common;
using Umbraco.Extensions;

namespace BroudoHoldings.Helpers;

/// <summary>Site-wide lookups (settings, pages, projects) and the display texts of project fields.</summary>
public static class Site
{
    public static IPublishedContent? Settings(this UmbracoHelper umbraco)
        => umbraco.ContentAtRoot().FirstOrDefault(item => item.ContentType.Alias == "SiteSettings");

    public static IPublishedContent? Home(this UmbracoHelper umbraco)
        => umbraco.ContentAtRoot().FirstOrDefault(item => item.ContentType.Alias == "HomePage");

    /// <summary>The first page of a type directly under the home page (e.g. "ContactPage").</summary>
    public static IPublishedContent? Section(this UmbracoHelper umbraco, string alias)
        => umbraco.Home()?.Children().FirstOrDefault(page => page.ContentType.Alias == alias);

    public static List<IPublishedContent> Projects(this UmbracoHelper umbraco)
        => umbraco.Section("ProjectsPage")?.Children().Where(page => page.ContentType.Alias == "ProjectPage").ToList() ?? [];

    public static List<IPublishedContent> Markets(this UmbracoHelper umbraco)
        => umbraco.Section("MarketsPage")?.Children().Where(page => page.ContentType.Alias == "MarketPage").ToList() ?? [];

    public static IPublishedContent? Market(this IPublishedContent project) => project.Value<IPublishedContent>("market");

    public static List<IPublishedContent> ProjectsIn(this UmbracoHelper umbraco, IPublishedContent market)
        => umbraco.Projects().Where(project => project.Market()?.Key == market.Key).ToList();

    /// <summary>"Atlanta, GA": the market's short name, or its page name.</summary>
    public static string MarketName(this IPublishedContent market)
        => market.Value<string>("shortName") is { Length: > 0 } shortName ? shortName : market.Name;

    public static string FounderName(this IPublishedContent? settings)
        => settings?.Value<string>("founderName") is { Length: > 0 } name ? name : "[Founder Name]";

    /// <summary>Replaces {founder} in an editor's text with the founder's name.</summary>
    public static string? WithFounder(this string? text, IPublishedContent? settings)
        => text?.Replace("{founder}", settings.FounderName());

    public static string NavigationLabel(this IPublishedContent page)
        => page.Value<string>("navigationLabel") is { Length: > 0 } label ? label : page.Name;

    /// <summary>Navigation links from a Block List of NavigationLinkBlock in the site settings.</summary>
    public static List<(string Label, string Url)> Links(this IPublishedContent? settings, string alias)
        => settings?.Value<BlockListModel>(alias)?
            .Select(item => (Label: item.Content.Value<string>("label") ?? "", Url: item.Content.Value<IEnumerable<Link>>("link")?.FirstOrDefault()?.Url ?? ""))
            .Where(link => link.Label != "" && link.Url != "")
            .ToList() ?? [];

    public static string ProjectType(string? value) => value switch
    {
        "renovation" => "Renovation",
        _ => "New construction",
    };

    public static string ProjectStatus(string? value) => value switch
    {
        "planning" => "Planning",
        "completed" => "Completed",
        "sold" => "Sold",
        "forSale" => "For sale",
        _ => "In progress",
    };

    public static readonly (string Value, string Label)[] ProjectTypes = [("newConstruction", "New construction"), ("renovation", "Renovation")];

    public static readonly (string Value, string Label)[] ProjectStatuses = [("planning", "Planning"), ("inProgress", "In progress"), ("completed", "Completed"), ("sold", "Sold"), ("forSale", "For sale")];

    /// <summary>"2,400 sq ft · 4 bd · 3.5 ba · 2025": the facts line of a project card.</summary>
    public static string CardFacts(this IPublishedContent project)
    {
        var parts = new List<string>();
        if (project.Value<int?>("livingArea") is > 0 and var area)
        {
            parts.Add(area.ToString("N0", CultureInfo.InvariantCulture) + " sq ft");
        }

        if (project.Value<int?>("bedrooms") is > 0 and var bedrooms)
        {
            parts.Add(bedrooms + " bd");
        }

        if (project.Value<decimal?>("bathrooms") is > 0 and var bathrooms)
        {
            parts.Add(bathrooms.ToString("0.#", CultureInfo.InvariantCulture) + " ba");
        }

        if (project.Value<int?>("year") is > 0 and var year)
        {
            parts.Add(year.ToString());
        }

        return string.Join(" · ", parts);
    }

    public static string MonthYear(DateTime? date) => date is { } value && value > DateTime.MinValue
        ? value.ToString("MMMM yyyy", CultureInfo.InvariantCulture)
        : "—";

    public static string WhatsAppUrl(this IPublishedContent? settings)
        => "https://wa.me/" + (settings?.Value<string>("whatsAppNumber") is { Length: > 0 } number ? new string(number.Where(char.IsDigit).ToArray()) : "");
}
