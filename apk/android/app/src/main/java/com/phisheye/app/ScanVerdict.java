package com.phisheye.app;

public class ScanVerdict {
    public final String url;
    public final String finalUrl;
    public final String level;
    public final int score;
    public final boolean safe;
    public final String headline;
    public final String summary;
    public final String action;
    public final boolean https;
    public final boolean blocked;
    public final boolean caution;
    public String payload = "";

    public ScanVerdict(String url, String finalUrl, String level, int score, boolean safe, String headline, String summary, String action) {
        this.url = url;
        this.finalUrl = finalUrl == null || finalUrl.isEmpty() ? url : finalUrl;
        this.level = level == null ? "" : level.toUpperCase();
        this.score = score;
        this.safe = safe;
        this.headline = clean(headline, "Check complete.");
        this.summary = clean(summary, this.headline);
        this.action = clean(action, "Do not enter a password, OTP, or card number.");
        this.https = this.finalUrl.startsWith("https://");
        this.blocked = this.level.equals("HIGH") || this.level.equals("CRITICAL") || score >= 50;
        this.caution = this.level.equals("MEDIUM");
    }

    private static String clean(String value, String fallback) {
        if (value == null) return fallback;
        String text = value.trim();
        if (text.isEmpty() || text.startsWith("{") || text.startsWith("[")) return fallback;
        return text;
    }
}
