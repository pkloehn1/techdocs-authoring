internal static class LogLineFilter
{
    // Loop through the lines and add each one that matches to the list.
    public static List<string> Matching(IEnumerable<string> lines)
    {
        List<string> hits = [];
        foreach (string line in lines)
        {
            if (Timestamped.IsMatch(line))
            {
                hits.Add(line);
            }
        }

        return hits;
    }

    private static readonly Regex Timestamped =
        new(@"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s{1,2}(?!\[)(.+)$", RegexOptions.Compiled);
}
