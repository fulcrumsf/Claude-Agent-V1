---
title: "Telemetry OTLP API Overview Google Cloud Observability"
type: "api-doc"
category: "app-dev"
tags:
  - app-dev
  - telemetry
  - opentelemetry
  - gcp
  - api-docs
created: 2026-05-12
source: local
---

This document describes the Telemetry (OTLP) API, which implements the [OpenTelemetry Line Protocol](https://opentelemetry.io/docs/specs/otlp). This API is designed for use with applications that are instrumented by using one of the [OpenTelemetry SDKs](https://opentelemetry.io/docs/languages/) or that use any OpenTelemetry Collector.

OpenTelemetry is a Google Cloud-supported open source project with Google Cloud engineers staffed to ensure support for ingesting and visualizing your telemetry.

To learn more about this API, see the following reference documents:

- [v1.traces overview](https://docs.cloud.google.com/stackdriver/docs/reference/telemetry/v1.traces)
- [v1.metrics overview](https://docs.cloud.google.com/stackdriver/docs/reference/telemetry/v1.metrics)
- [v1.logs overview](https://docs.cloud.google.com/stackdriver/docs/reference/telemetry/v1.logs)

## Best practices

When instrumenting your applications to send trace data to your Google Cloud project, we recommend that you use an exporter that writes OTLP-formatted data to a [Collector](https://opentelemetry.io/docs/collector/), which then sends your trace data to the Telemetry API. In your collector, specify only the root URL:

```
exporters:
  otlphttp:
    encoding: proto
    endpoint: https://telemetry.googleapis.com
```

OpenTelemetry detects the data type and automatically appends `/v1/traces`, `/v1/metrics`, or `/v1/logs` as appropriate. For more information, see [OTLP/HTTP Request](https://opentelemetry.io/docs/specs/otlp#otlphttp-request).

For examples that export trace or metric data to the Telemetry API, see the following documents:

- [Overview of collector-based instrumentation samples](https://docs.cloud.google.com/stackdriver/docs/instrumentation/setup/sample-overview).
- [OTLP metric ingestion overview](https://docs.cloud.google.com/stackdriver/docs/otlp-metrics/overview).

When you can't use a collector, you can use an OpenTelemetry library that contains an in-process OTLP exporter to send telemetry to the Telemetry API. To learn how to directly export trace data, see [Cloud Trace exporter to the OTLP endpoint](https://docs.cloud.google.com/stackdriver/docs/instrumentation/migrate-to-otlp-endpoints).

## Authentication

You must configure your exporters with the credentials necessary to send data to your Google Cloud project. For example, when you use collectors, typically you also use the `googleclientauth` extension to authenticate with Google credentials.

For an example of authentication when using direct export of trace data, see [Configure authentication](https://docs.cloud.google.com/stackdriver/docs/instrumentation/migrate-to-otlp-endpoints#auth). This example illustrates how to configure the exporter with your Google Cloud [Application Default Credentials (ADC)](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc) and add a language-specific Google Auth Library to your application.

## VPC Service Controls support

The Telemetry API service, whose service name is `telemetry.googleapis.com`, is a VPC Service Controls-supported service. Any VPC Service Controls restrictions that you create for the Telemetry API service apply only to that service. Those restrictions don't apply to any other services, including those like the `cloudtrace.googleapis.com` service, which can also ingest trace data.

For more information, see the following:

- [VPC Service Controls documentation](https://docs.cloud.google.com/vpc-service-controls/docs).
- [Supported products and limitations](https://docs.cloud.google.com/vpc-service-controls/docs/supported-products).
