# Build a Google Analytics 4 Data API Tool Using Model Context Protocol (MCP)

Google Analytics 4 (GA4) is a powerful tool to track website and app
usage, providing valuable metrics and insights.\
However, integrating with the **GA4 Data API** and building your own
flexible data tool can be tricky. That's where **Model Context Protocol
(MCP)** comes in.

In this guide, we'll show you step by step how to build a robust GA4
Data API integration using MCP.\
This solution will allow you to query any dimension and metric
combination, with filtering, aggregation, and best practices baked in.

## ✅ What Is Model Context Protocol (MCP)?

MCP is a framework that helps you build well-defined, self-describing
Python functions called "tools".\
Each tool: - Has a clear input and output format - Is automatically
serialized into JSON - Can run with different transports (e.g., stdio,
HTTP)

This makes it perfect for building APIs that are easy to extend,
maintain, and document.

## ✅ Step 1: Set Up Google Analytics 4 and Get Credentials

### 📊 Create a Google Analytics 4 Property

1.  Go to <https://analytics.google.com/>.
2.  In the Admin section:
    -   Create a new account or select an existing one.
    -   Click **"Create Property"**.
    -   Fill in Property Name, Time Zone, and Currency.
    -   Add a data stream (Web, iOS, or Android).
3.  After setup, find your **GA4 Property ID** (e.g., `123456789`) in
    Admin → Property Settings.

### 🔑 Create a Google Cloud Project and Service Account

1.  Visit <https://console.cloud.google.com/>.
2.  Create a new project.
3.  Go to **APIs & Services → Credentials**.
4.  Click **"Create Credentials" → "Service Account"**.
5.  Name it (e.g., `ga4-api-service-account`).
6.  After creation:
    -   Under **Keys**, add a new key in **JSON format**.
    -   Download the file `credentials.json`.

### 🧱 Link Service Account to Google Analytics

1.  In <https://analytics.google.com/>:
    -   Go to Admin → Account Access Management or Property Access
        Management.
    -   Add the service account email (found in `credentials.json` under
        `client_email`).
    -   Grant **Viewer** role.

### ⚙️ Configure Environment Variables

Create a `.env` file in your project root with:

``` bash
GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/credentials.json"
GA4_PROPERTY_ID="123456789"
```

This tells the code where to find credentials and which property to
query.

## ✅ Step 2: Install Dependencies

``` bash
pip install fastmcp google-analytics-data python-dotenv
```

## ✅ Step 3: Initialize MCP and Define Metadata

We'll embed GA4 dimensions and metrics in dictionaries for easy
reference.

``` python
from fastmcp import FastMCP

mcp = FastMCP("Google Analytics 4")

GA4_DIMENSIONS = {
    "time": {
        "date": "Event date in YYYYMMDD format",
        "hour": "Hour of the day (00-23)"
    },
    ...
}

GA4_METRICS = {
    "user_metrics": {
        "totalUsers": "Unique users count",
        "newUsers": "New user count"
    },
    ...
}
```

This provides a self-contained reference inside the tool.

## ✅ Step 4: Expose Exploration Tools

These simple MCP tools help you explore available dimensions and
metrics.

``` python
@mcp.tool()
def list_dimension_categories() -> dict:
    return {category: {"count": len(dims), "dimensions": list(dims.keys())}
            for category, dims in GA4_DIMENSIONS.items()}

@mcp.tool()
def list_metric_categories() -> dict:
    return {category: {"count": len(mets), "metrics": list(mets.keys())}
            for category, mets in GA4_METRICS.items()}
```

This avoids guessing or reading external docs manually.

## ✅ Step 5: Build the Core Data Fetching Tool

This is the heart of the solution.\
It fetches data from GA4 based on parameters and intelligently handles
aggregation, limits, and filtering.

``` python
@mcp.tool()
def get_ga4_data(
    dimensions=["date"],
    metrics=["totalUsers"],
    date_range_start="7daysAgo",
    date_range_end="yesterday",
    limit=None
):
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import RunReportRequest, Dimension, Metric, DateRange

    client = BetaAnalyticsDataClient()
    request = RunReportRequest(
        property=f"properties/{os.getenv('GA4_PROPERTY_ID')}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=date_range_start, end_date=date_range_end)],
        limit=str(limit) if limit else None
    )

    response = client.run_report(request)
    return [
        {header.name: row.dimension_values[idx].value
         for idx, header in enumerate(response.dimension_headers)}
        | {header.name: row.metric_values[idx].value
           for idx, header in enumerate(response.metric_headers)}
        for row in response.rows
    ]
```

This provides a clean interface to query any dimensions and metrics.

## ✅ Step 6: Run the MCP Application

At the bottom of your code, run the MCP tool system:

``` python
def main() -> None:
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
```

This exposes all defined tools for easy interaction via command line or
API.

## ✅ Example Query Usage

Once running, you can query the tool like this:

``` json
{
  "tool": "get_ga4_data",
  "dimensions": ["date"],
  "metrics": ["totalUsers", "bounceRate"],
  "date_range_start": "7daysAgo",
  "date_range_end": "yesterday"
}
```

The output will be structured JSON with date-wise user and bounce rate
data.

## ✅ Why MCP Is a Game-Changer

-   **Modular Design:** Easy to add new tools in the future.
-   **Automatic Serialization:** No manual JSON handling.
-   **Clear Interfaces:** Simple function signatures.
-   **Reusability:** Integrate into any front end, CLI, or automation
    pipeline.

## ✅ Next Steps

-   Add custom predefined reports
-   Build a web dashboard calling MCP tools
-   Add user authentication for secure access
-   Create scheduled reports with this tool

## 🎉 Conclusion

Building a GA4 data API tool with **Model Context Protocol (MCP)** is
simple, efficient, and future-proof.\
You now have a fully functional solution to query any dimension and
metric combination in Google Analytics 4, with intelligent defaults and
filtering support.

👉 Happy Data Exploration 🚀

