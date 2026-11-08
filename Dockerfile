# Broudo Holdings website — container image for Render (see render.yaml).
# Everything that must survive a deploy (database, uploaded media, login keys) lives on the persistent
# disk mounted at /var/data; see appsettings.Production.json.
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY BroudoHoldings.csproj Directory.Packages.props ./
RUN dotnet restore BroudoHoldings.csproj
COPY . .
RUN dotnet publish BroudoHoldings.csproj -c Release -o /app --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=build /app ./
# Read at runtime from the content root: the content model (uSync) and the default content (first start only)
COPY uSync ./uSync
COPY Seeding/DefaultContent.json ./Seeding/DefaultContent.json
# DOTNET_gcServer=0: the workstation GC holds much less memory than the server GC
ENV ASPNETCORE_ENVIRONMENT=Production \
    ASPNETCORE_HTTP_PORTS=10000 \
    ASPNETCORE_FORWARDEDHEADERS_ENABLED=true \
    DOTNET_gcServer=0
EXPOSE 10000
ENTRYPOINT ["dotnet", "BroudoHoldings.dll"]
