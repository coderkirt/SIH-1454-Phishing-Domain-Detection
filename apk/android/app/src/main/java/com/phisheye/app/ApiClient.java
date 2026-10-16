package com.phisheye.app;

import android.content.Context;
import android.content.SharedPreferences;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class ApiClient {
    private static final Map<String, ScanVerdict> CACHE = new ConcurrentHashMap<>();
    private static final String PREFS = "phisheye";

    public static void saveBase(Context context, String url) {
        if (url == null) return;
        String clean = url.trim().replaceAll("/+$", "");
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putString("api_url", clean).apply();
    }

    public static List<String> bases(Context context) {
        LinkedHashSet<String> set = new LinkedHashSet<>();
        SharedPreferences prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        add(set, prefs.getString("api_url", null));
        add(set, readAssetConfig(context));
        add(set, "http://10.12.4.184:8000");
        add(set, "http://172.16.33.52:8000");
        add(set, "http://192.168.137.1:8000");
        add(set, "http://10.0.2.2:8000");
        return new ArrayList<>(set);
    }

    public static String postQrImage(Context context, byte[] image) throws Exception {
        return postFirst(context, (base) -> multipart(base + "/api/v1/analyze/qr", image));
    }

    public static String postContent(Context context, String text) throws Exception {
        JSONObject body = new JSONObject();
        body.put("source_type", "text");
        body.put("text", text == null ? "" : text);
        return postFirst(context, (base) -> postJson(base + "/api/v1/analyze/content", body.toString()));
    }

    private interface Attempt {
        String run(String base) throws Exception;
    }

    private static String postFirst(Context context, Attempt attempt) throws Exception {
        Exception last = null;
        for (String base : bases(context)) {
            try {
                String raw = attempt.run(base);
                saveBase(context, base);
                return raw;
            } catch (Exception error) {
                last = error;
            }
        }
        throw last == null ? new IllegalStateException("No API address configured") : last;
    }

    private static String postJson(String endpoint, String json) throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(endpoint).openConnection();
        connection.setConnectTimeout(2500);
        connection.setReadTimeout(20000);
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        try (OutputStream output = connection.getOutputStream()) {
            output.write(bytes);
        }
        return readResponse(connection);
    }

    private static String multipart(String endpoint, byte[] image) throws Exception {
        String boundary = "phisheye-" + System.currentTimeMillis();
        HttpURLConnection connection = (HttpURLConnection) new URL(endpoint).openConnection();
        connection.setConnectTimeout(2500);
        connection.setReadTimeout(20000);
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "multipart/form-data; boundary=" + boundary);
        connection.setDoOutput(true);
        try (OutputStream output = connection.getOutputStream()) {
            output.write(("--" + boundary + "\r\n").getBytes(StandardCharsets.UTF_8));
            output.write("Content-Disposition: form-data; name=\"file\"; filename=\"qr.png\"\r\n".getBytes(StandardCharsets.UTF_8));
            output.write("Content-Type: image/png\r\n\r\n".getBytes(StandardCharsets.UTF_8));
            output.write(image);
            output.write(("\r\n--" + boundary + "--\r\n").getBytes(StandardCharsets.UTF_8));
        }
        return readResponse(connection);
    }

    private static String readResponse(HttpURLConnection connection) throws Exception {
        int code = connection.getResponseCode();
        InputStream stream = code >= 400 ? connection.getErrorStream() : connection.getInputStream();
        String raw = read(stream);
        if (code >= 400) throw new IllegalStateException(errorDetail(raw, code));
        return raw;
    }

    private static String errorDetail(String raw, int code) {
        try {
            String detail = new JSONObject(raw).optString("detail", "");
            if (!detail.isEmpty()) return detail;
        } catch (Exception ignored) {
        }
        return "API HTTP " + code;
    }

    public static ScanVerdict checkUrl(Context context, String pageUrl) throws Exception {
        ScanVerdict cached = CACHE.get(pageUrl);
        if (cached != null) return cached;
        Exception last = null;
        for (String base : bases(context)) {
            try {
                ScanVerdict verdict = postCheck(base, pageUrl);
                saveBase(context, base);
                CACHE.put(pageUrl, verdict);
                if (verdict.finalUrl != null) CACHE.put(verdict.finalUrl, verdict);
                return verdict;
            } catch (Exception error) {
                last = error;
            }
        }
        throw last == null ? new IllegalStateException("No API address configured") : last;
    }

    private static ScanVerdict postCheck(String base, String pageUrl) throws Exception {
        URL endpoint = new URL(base + "/api/v1/threat/check-url");
        HttpURLConnection connection = (HttpURLConnection) endpoint.openConnection();
        connection.setConnectTimeout(2500);
        connection.setReadTimeout(12000);
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);
        JSONObject body = new JSONObject();
        body.put("url", pageUrl);
        body.put("view", "both");
        byte[] bytes = body.toString().getBytes(StandardCharsets.UTF_8);
        try (OutputStream output = connection.getOutputStream()) {
            output.write(bytes);
        }
        int code = connection.getResponseCode();
        InputStream stream = code >= 400 ? connection.getErrorStream() : connection.getInputStream();
        String raw = read(stream);
        if (code >= 400) throw new IllegalStateException("API HTTP " + code + " " + raw);
        JSONObject data = new JSONObject(raw);
        JSONObject simple = data.optJSONObject("simple_view");
        Object explanation = data.opt("explanation");
        String headline = plain(explanation instanceof JSONObject ? ((JSONObject) explanation).opt("headline") : explanation);
        String summary = plain(explanation instanceof JSONObject ? ((JSONObject) explanation).opt("what") : "");
        String action = plain(explanation instanceof JSONObject ? ((JSONObject) explanation).opt("what_to_do") : "");
        if (simple != null) {
            String warning = plain(simple.opt("warning"));
            if (warning.isEmpty()) warning = plain(simple.opt("summary"));
            if (!warning.isEmpty()) summary = warning;
            String simpleHeadline = plain(simple.opt("headline"));
            if (!simpleHeadline.isEmpty() && !simpleHeadline.contains("{")) headline = simpleHeadline;
        }
        if (summary.isEmpty()) summary = headline;
        ScanVerdict verdict = new ScanVerdict(
            data.optString("url", pageUrl),
            data.optString("final_url", data.optString("url", pageUrl)),
            data.optString("risk_level", ""),
            data.optInt("risk_score", 0),
            data.optBoolean("safe", false),
            headline,
            summary,
            action
        );
        verdict.payload = raw;
        return verdict;
    }

    private static String plain(Object value) {
        if (value == null || value == JSONObject.NULL) return "";
        if (value instanceof JSONObject) {
            JSONObject object = (JSONObject) value;
            String what = plain(object.opt("what"));
            if (!what.isEmpty()) return what;
            return plain(object.opt("headline"));
        }
        if (value instanceof JSONArray) {
            JSONArray array = (JSONArray) value;
            StringBuilder builder = new StringBuilder();
            int limit = Math.min(array.length(), 2);
            for (int index = 0; index < limit; index++) {
                String line = plain(array.opt(index));
                if (line.isEmpty()) continue;
                if (builder.length() > 0) builder.append(' ');
                builder.append(line);
            }
            return builder.toString();
        }
        String text = String.valueOf(value).trim();
        if (text.startsWith("{")) {
            try {
                return plain(new JSONObject(text));
            } catch (Exception ignored) {
                return "";
            }
        }
        if (text.startsWith("[")) return "";
        return text;
    }

    private static String readAssetConfig(Context context) {
        try (InputStream input = context.getAssets().open("public/api-config.json")) {
            JSONObject json = new JSONObject(read(input));
            return json.optString("apiUrl", null);
        } catch (Exception ignored) {
            return null;
        }
    }

    private static void add(LinkedHashSet<String> set, String value) {
        if (value == null) return;
        String clean = value.trim().replaceAll("/+$", "");
        if (clean.startsWith("http")) set.add(clean);
    }

    private static String read(InputStream stream) throws Exception {
        if (stream == null) return "";
        BufferedReader reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8));
        StringBuilder builder = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) builder.append(line);
        return builder.toString();
    }
}
