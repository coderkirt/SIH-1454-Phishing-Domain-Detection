package com.phisheye.app;

import android.app.Activity;
import android.app.role.RoleManager;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.provider.Settings;
import android.webkit.JavascriptInterface;

public class NativeBridge {
    private final Activity activity;

    public NativeBridge(Activity activity) {
        this.activity = activity;
    }

    @JavascriptInterface
    public void openCheckedUrl(String url) {
        if (url == null || url.isEmpty()) return;
        Intent intent = new Intent(activity, BrowserActivity.class);
        intent.setAction(Intent.ACTION_VIEW);
        intent.setData(Uri.parse(url));
        intent.putExtra("skip_scan", true);
        activity.startActivity(intent);
    }

    @JavascriptInterface
    public void setApiUrl(String url) {
        ApiClient.saveBase(activity, url);
    }

    @JavascriptInterface
    public void openAccessibility() {
        Intent intent = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        activity.startActivity(intent);
    }

    @JavascriptInterface
    public void requestBrowserRole() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            RoleManager roles = activity.getSystemService(RoleManager.class);
            if (roles != null && roles.isRoleAvailable(RoleManager.ROLE_BROWSER) && !roles.isRoleHeld(RoleManager.ROLE_BROWSER)) {
                activity.startActivityForResult(roles.createRequestRoleIntent(RoleManager.ROLE_BROWSER), 91);
                return;
            }
        }
        Intent intent = new Intent(Settings.ACTION_MANAGE_DEFAULT_APPS_SETTINGS);
        activity.startActivity(intent);
    }
}
