package com.phisheye.app;

import android.accessibilityservice.AccessibilityService;
import android.content.Intent;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import java.util.Arrays;
import java.util.List;

public class LinkGuardService extends AccessibilityService {
    private static final List<String> URL_IDS = Arrays.asList(
        "com.android.chrome:id/url_bar",
        "com.android.chrome:id/search_box_text",
        "org.mozilla.firefox:id/url_bar_title",
        "org.mozilla.firefox:id/mozac_browser_toolbar_url_view",
        "com.sec.android.app.sbrowser:id/location_bar_edit_text",
        "com.microsoft.emmx:id/url_bar",
        "com.opera.browser:id/url_field"
    );
    private final Handler handler = new Handler(Looper.getMainLooper());
    private String last = "";
    private Runnable pending;

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null) return;
        String url = findUrl(root);
        root.recycle();
        if (url == null || url.equals(last) || url.startsWith("chrome://") || url.startsWith("about:")) return;
        last = url;
        if (pending != null) handler.removeCallbacks(pending);
        String captured = url;
        pending = () -> inspect(captured);
        handler.postDelayed(pending, 400);
    }

    @Override
    public void onInterrupt() {}

    private void inspect(String url) {
        new Thread(() -> {
            try {
                ScanVerdict verdict = ApiClient.checkUrl(this, url);
                if (!verdict.blocked) return;
                performGlobalAction(GLOBAL_ACTION_BACK);
                Intent intent = new Intent(this, BrowserActivity.class);
                intent.setAction(Intent.ACTION_VIEW);
                intent.setData(Uri.parse(verdict.finalUrl));
                intent.putExtra("from_guard", false);
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
                startActivity(intent);
            } catch (Exception ignored) {
                /* keep browsing if API is down rather than freezing Chrome */
            }
        }).start();
    }

    private String findUrl(AccessibilityNodeInfo root) {
        for (String id : URL_IDS) {
            List<AccessibilityNodeInfo> nodes = root.findAccessibilityNodeInfosByViewId(id);
            if (nodes == null) continue;
            for (AccessibilityNodeInfo node : nodes) {
                CharSequence text = node.getText();
                node.recycle();
                if (text == null) continue;
                String value = text.toString().trim();
                if (value.startsWith("http://") || value.startsWith("https://")) return value;
                if (value.contains(".") && !value.contains(" ")) return "https://" + value;
            }
        }
        return null;
    }
}
