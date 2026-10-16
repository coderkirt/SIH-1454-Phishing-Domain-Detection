package com.phisheye.app;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.webkit.WebView;
import androidx.core.splashscreen.SplashScreen;
import com.getcapacitor.BridgeActivity;
import org.json.JSONObject;

public class MainActivity extends BridgeActivity {
    private int reportAttempts = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        SplashScreen.installSplashScreen(this).setKeepOnScreenCondition(() -> false);
        super.onCreate(savedInstanceState);
        attachBridge();
        deliverReport(getIntent(), 400);
    }

    @Override
    public void onStart() {
        super.onStart();
        attachBridge();
    }

    @Override
    public void onResume() {
        super.onResume();
        deliverReport(getIntent(), 200);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        reportAttempts = 0;
        deliverReport(intent, 200);
    }

    private void attachBridge() {
        if (getBridge() == null) return;
        WebView webView = getBridge().getWebView();
        if (webView == null) return;
        webView.addJavascriptInterface(new NativeBridge(this), "PhishEyeNative");
    }

    private void deliverReport(Intent intent, int delayMs) {
        if (intent == null || intent.getBooleanExtra("report_sent", false)) return;
        String json = intent.getStringExtra("scan_json");
        if (json == null || json.isEmpty()) return;
        WebView webView = getBridge() != null ? getBridge().getWebView() : null;
        if (webView == null) {
            retryReport(intent);
            return;
        }
        String js = "(function(){if(!window.__phisheyeReportReady)return 'wait';"
            + "window.dispatchEvent(new CustomEvent('phisheye-report',{detail:"
            + JSONObject.quote(json) + "}));return 'ok';})()";
        webView.postDelayed(() -> {
            if (intent.getBooleanExtra("report_sent", false)) return;
            webView.evaluateJavascript(js, value -> {
                if (value != null && value.contains("ok")) {
                    intent.putExtra("report_sent", true);
                    reportAttempts = 0;
                } else {
                    retryReport(intent);
                }
            });
        }, delayMs);
    }

    private void retryReport(Intent intent) {
        if (intent.getBooleanExtra("report_sent", false) || reportAttempts >= 25) return;
        reportAttempts += 1;
        new Handler(Looper.getMainLooper()).postDelayed(() -> deliverReport(intent, 250), 250);
    }
}
