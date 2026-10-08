// Retry policy for the upload path. The numbers come from the provider's
// published rate limits, not from taste.
internal static class UploadRetry
{
    // The provider rejects a seventh request in any 10s window.
    private const int MaxAttempts = 6;

    // Jittered so a fleet restart does not synchronise its retries.
    private static readonly TimeSpan BaseDelay = TimeSpan.FromMilliseconds(250);

    private const int ChunkBytes = 8192;

    public static TimeSpan DelayFor(int attempt) =>
        BaseDelay * Math.Pow(2, attempt - 1);
}
