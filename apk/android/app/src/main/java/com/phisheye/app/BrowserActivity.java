package com.phisheye.app;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class BrowserActivity extends AppCompatActivity {
    private static final Pattern HTTP_URL = Pattern.compile("https?://[^\\s<>\"']+", Pattern.CASE_INSENSITIVE);
    private WebView web;
    private TextView address;
    private TextView statusChip;
    private ImageView lockIcon;
    private ProgressBar progress;
    private View blockPanel;
    private TextView blockScore;
    private TextView blockLevel;
    private TextView blockTitle;
    private TextView blockBody;
    private TextView blockAction;
    private TextView blockUrl;
    private TextView blockMeta;
    private String approved;
    private String currentUrl;
    private boolean fromGuard;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_browser);
        web = findViewById(R.id.web);
        address = findViewById(R.id.address);
        statusChip = findViewById(R.id.statusChip);
        lockIcon = findViewById(R.id.lockIcon);
        progress = findViewById(R.id.progress);
        blockPanel = findViewById(R.id.blockPanel);
        blockScore = findViewById(R.id.blockScore);
        blockLevel = findViewById(R.id.blockLevel);
        blockTitle = findViewById(R.id.blockTitle);
        blockBody = findViewById(R.id.blockBody);
        blockAction = findViewById(R.id.blockAction);
        blockUrl = findViewById(R.id.blockUrl);
        blockMeta = findViewById(R.id.blockMeta);
        findViewById(R.id.keepClosed).setOnClickListener(v -> finish());
        findViewById(R.id.btnReload).setOnClickListener(v -> {
            if (currentUrl != null) scanThenLoad(currentUrl);
            else if (web.getUrl() != null) web.reload();
        });
        findViewById(R.id.btnBack).setOnClickListener(v -> {
            if (web.canGoBack()) web.goBack();
        });
        findViewById(R.id.btnForward).setOnClickListener(v -> {
            if (web.canGoForward()) web.goForward();
        });
        findViewById(R.id.btnHome).setOnClickListener(v -> {
            startActivity(new Intent(this, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP));
            finish();
        });
        findViewById(R.id.btnClose).setOnClickListener(v -> finish());

        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String next = request.getUrl().toString();
                if (next.equals(approved) || next.startsWith("about:")) return false;
                scanThenLoad(next);
                return true;
            }

            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                showAddress(url);
            }
        });

        openIncoming(getIntent());
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        openIncoming(intent);
    }

    private void openIncoming(Intent intent) {
        fromGuard = intent.getBooleanExtra("from_guard", false);
        String url = extractUrl(intent);
        if (intent.getBooleanExtra("skip_scan", false) && url != null) {
            approved = url;
            currentUrl = url;
            progress.setVisibility(View.GONE);
            showAddress(url);
            setStatus("Opened", 0xFF81C995);
            web.loadUrl(url);
            return;
        }
        if (url != null) {
            scanThenLoad(url);
            return;
        }
        Uri image = sharedImage(intent);
        String shared = sharedText(intent);
        if (image != null || (shared != null && !shared.trim().isEmpty())) {
            address.setText(image != null ? "Reading QR" : "Checking message");
            progress.setVisibility(View.VISIBLE);
            setStatus("Checking", 0xFF9AA0A6);
            new Thread(() -> analyzeShared(image, shared)).start();
            return;
        }
        address.setText("No link found");
        progress.setVisibility(View.GONE);
    }

    private void analyzeShared(Uri image, String shared) {
        try {
            String raw = image != null
                ? ApiClient.postQrImage(this, readBytes(image))
                : ApiClient.postContent(this, shared);
            runOnUiThread(() -> {
                Intent report = new Intent(this, MainActivity.class);
                report.putExtra("scan_json", raw);
                report.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
                startActivity(report);
                finish();
            });
        } catch (Exception error) {
            String message = error.getMessage() == null ? "No link found" : error.getMessage();
            runOnUiThread(() -> {
                progress.setVisibility(View.GONE);
                address.setText("No link found");
                setStatus("Offline", 0xFFF28B82);
                blockScore.setText("—");
                blockLevel.setText("NOT READ");
                blockTitle.setText("Could not read that QR");
                blockBody.setText(message);
                blockAction.setText("Use a sharper photo of the whole code, or paste the link.");
                blockUrl.setText(shared == null ? "" : shared);
                blockMeta.setText("Every QR in the image is checked when the photo can be read.");
                blockPanel.setVisibility(View.VISIBLE);
            });
        }
    }

    private byte[] readBytes(Uri uri) throws Exception {
        try (InputStream input = getContentResolver().openInputStream(uri)) {
            if (input == null) throw new IllegalStateException("Could not open that image.");
            ByteArrayOutputStream output = new ByteArrayOutputStream();
            byte[] buffer = new byte[8192];
            int read;
            int total = 0;
            while ((read = input.read(buffer)) != -1) {
                total += read;
                if (total > 5_000_000) throw new IllegalStateException("Image is too large (max 5 MB).");
                output.write(buffer, 0, read);
            }
            return output.toByteArray();
        }
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack() && blockPanel.getVisibility() != View.VISIBLE) {
            web.goBack();
            return;
        }
        super.onBackPressed();
    }

    private void scanThenLoad(String url) {
        approved = null;
        currentUrl = url;
        runOnUiThread(() -> {
            blockPanel.setVisibility(View.GONE);
            progress.setVisibility(View.VISIBLE);
            showAddress(url);
            setStatus("Checking", 0xFF9AA0A6);
        });
        new Thread(() -> {
            try {
                ScanVerdict verdict = ApiClient.checkUrl(this, url);
                runOnUiThread(() -> apply(verdict));
            } catch (Exception error) {
                runOnUiThread(() -> {
                    progress.setVisibility(View.GONE);
                    setStatus("Offline", 0xFFF28B82);
                    showAddress(url);
                    blockScore.setText("—");
                    blockLevel.setText("OFFLINE");
                    blockTitle.setText("Can’t reach PhishEye");
                    blockBody.setText("This phone cannot talk to the security engine on your computer.");
                    blockAction.setText("Use the same Wi-Fi, keep the API running on port 8000, then save that address in Guard.");
                    blockUrl.setText(url);
                    blockMeta.setText("Connection: not checked");
                    blockPanel.setVisibility(View.VISIBLE);
                });
            }
        }).start();
    }

    private void apply(ScanVerdict verdict) {
        progress.setVisibility(View.GONE);
        showAddress(verdict.finalUrl);
        if ((verdict.blocked || verdict.caution) && verdict.payload != null && !verdict.payload.isEmpty()) {
            web.stopLoading();
            Intent report = new Intent(this, MainActivity.class);
            report.putExtra("scan_json", verdict.payload);
            report.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(report);
            return;
        }
        if (verdict.blocked) {
            web.stopLoading();
            web.loadUrl("about:blank");
            setStatus("Dangerous", 0xFFF28B82);
            blockScore.setText(verdict.score + "/100");
            blockLevel.setText(verdict.level.isEmpty() ? "DANGEROUS" : verdict.level);
            blockTitle.setText("Deceptive site ahead");
            blockBody.setText(verdict.summary);
            blockAction.setText(verdict.action);
            blockUrl.setText(verdict.finalUrl);
            blockMeta.setText(verdict.https ? "Connection: encrypted (HTTPS)" : "Connection: not encrypted");
            blockPanel.setVisibility(View.VISIBLE);
            return;
        }
        setStatus(verdict.caution ? "Caution" : "Secure", verdict.caution ? 0xFFFDD663 : 0xFF81C995);
        if (fromGuard && !verdict.caution) {
            finish();
            return;
        }
        approved = verdict.finalUrl;
        web.loadUrl(verdict.finalUrl);
    }

    private void setStatus(String label, int color) {
        statusChip.setText(label);
        statusChip.setTextColor(color);
        lockIcon.setColorFilter(color);
    }

    private void showAddress(String url) {
        address.setText(hostOf(url));
    }

    private String hostOf(String url) {
        try {
            String host = Uri.parse(url).getHost();
            if (host == null || host.isEmpty()) return url;
            return host.startsWith("www.") ? host.substring(4) : host;
        } catch (Exception error) {
            return url;
        }
    }

    private Uri sharedImage(Intent intent) {
        if (intent == null || !Intent.ACTION_SEND.equals(intent.getAction())) return null;
        Uri stream = null;
        if (Build.VERSION.SDK_INT >= 33) {
            stream = intent.getParcelableExtra(Intent.EXTRA_STREAM, Uri.class);
        } else {
            stream = intent.getParcelableExtra(Intent.EXTRA_STREAM);
        }
        if (stream == null && intent.getClipData() != null && intent.getClipData().getItemCount() > 0) {
            stream = intent.getClipData().getItemAt(0).getUri();
        }
        if (stream == null) return null;
        String type = intent.getType();
        if (type != null && !type.startsWith("image/")) return null;
        return stream;
    }

    private String sharedText(Intent intent) {
        if (intent == null) return null;
        if (Intent.ACTION_SEND.equals(intent.getAction())) {
            return intent.getStringExtra(Intent.EXTRA_TEXT);
        }
        return intent.getStringExtra("url");
    }

    private String extractUrl(Intent intent) {
        if (intent == null) return null;
        if (Intent.ACTION_SEND.equals(intent.getAction())) {
            return firstHttpUrl(intent.getStringExtra(Intent.EXTRA_TEXT));
        }
        Uri data = intent.getData();
        if (data != null) {
            String scheme = data.getScheme();
            if ("http".equals(scheme) || "https".equals(scheme)) return data.toString();
        }
        String extra = intent.getStringExtra("url");
        return firstHttpUrl(extra);
    }

    private String firstHttpUrl(String text) {
        if (text == null || text.isEmpty()) return null;
        Matcher matcher = HTTP_URL.matcher(text);
        if (matcher.find()) return matcher.group().replaceAll("[),.;]+$", "");
        return null;
    }
}
