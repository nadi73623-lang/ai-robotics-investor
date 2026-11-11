package com.airoboticsinvestor;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.Bundle;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;
import java.security.KeyStore;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import android.view.Gravity;
import android.view.View;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONObject;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.Duration;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class MainActivity extends Activity {
    private final ExecutorService io = Executors.newSingleThreadExecutor();
    private LinearLayout root;
    private TextView status, reportView;
    private android.content.SharedPreferences prefs;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        prefs = getSharedPreferences("robotics_read_config", MODE_PRIVATE);
        buildScreen();
    }

    private void buildScreen() {
        ScrollView scroll = new ScrollView(this);
        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(28, 28, 28, 28);
        scroll.addView(root);
        setContentView(scroll);

        TextView title = new TextView(this);
        title.setText("AI Robotics");
        title.setTextSize(26);
        title.setGravity(Gravity.CENTER_VERTICAL);
        root.addView(title);

        TextView subtitle = new TextView(this);
        subtitle.setText("Niezależny widok raportu inwestycyjnego • Balanced 1.3");
        subtitle.setTextSize(14);
        root.addView(subtitle);

        LinearLayout actions = new LinearLayout(this);
        Button refresh = new Button(this); refresh.setText("Pobierz raport");
        refresh.setOnClickListener(v -> loadReport());
        Button config = new Button(this); config.setText("Konfiguracja");
        config.setOnClickListener(v -> showConfig());
        actions.addView(refresh, new LinearLayout.LayoutParams(0, -2, 1));
        actions.addView(config, new LinearLayout.LayoutParams(0, -2, 1));
        root.addView(actions);

        status = new TextView(this); status.setTextSize(14); status.setPadding(0, 18, 0, 18);
        root.addView(status);
        reportView = new TextView(this); reportView.setTextSize(13);
        reportView.setTextIsSelectable(true);
        root.addView(reportView);
        status.setText(prefs.getString("url", "").isEmpty()
                ? "Skonfiguruj adres backendu i token tylko do odczytu."
                : "Gotowy do pobrania raportu.");
    }

    private void showConfig() {
        LinearLayout form = new LinearLayout(this); form.setOrientation(LinearLayout.VERTICAL);
        form.setPadding(24, 8, 24, 0);
        EditText url = new EditText(this); url.setSingleLine(true);
        url.setHint("https://twoj-worker.example.workers.dev");
        url.setText(prefs.getString("url", ""));
        EditText token = new EditText(this); token.setSingleLine(true);
        token.setHint("READ_TOKEN");
        token.setInputType(129);
        token.setText(readToken());
        form.addView(url); form.addView(token);
        new AlertDialog.Builder(this).setTitle("Połączenie tylko do odczytu")
            .setMessage("Adres bazowy Worker oraz osobny READ_TOKEN. Token nie jest wysyłany do logów.")
            .setView(form)
            .setNegativeButton("Anuluj", null)
            .setPositiveButton("Zapisz", (d, w) -> {
                String u = url.getText().toString().trim().replaceAll("/+$", "");
                String t = token.getText().toString().trim();
                if (!u.startsWith("https://") || t.isEmpty()) {
                    status.setText("Wymagany adres HTTPS i token READ_TOKEN.");
                    return;
                }
                try {
                    prefs.edit().putString("url", u).putString("token_enc", encryptToken(t)).remove("token").apply();
                    status.setText("Konfiguracja zapisana lokalnie (Android Keystore).");
                } catch (Exception ex) {
                    status.setText("Nie udało się bezpiecznie zapisać tokenu: " + ex.getClass().getSimpleName());
                }
            }).show();
    }

    private static final String KEY_ALIAS = "ai_robotics_read_token_v1";

    private SecretKey getOrCreateKey() throws Exception {
        KeyStore ks = KeyStore.getInstance("AndroidKeyStore");
        ks.load(null);
        java.security.Key existing = ks.getKey(KEY_ALIAS, null);
        if (existing instanceof SecretKey) return (SecretKey) existing;
        KeyGenerator generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
        generator.init(new KeyGenParameterSpec.Builder(KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setRandomizedEncryptionRequired(true)
                .build());
        return generator.generateKey();
    }

    private String encryptToken(String plain) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey());
        byte[] iv = cipher.getIV();
        byte[] encrypted = cipher.doFinal(plain.getBytes(StandardCharsets.UTF_8));
        byte[] packed = new byte[iv.length + encrypted.length];
        System.arraycopy(iv, 0, packed, 0, iv.length);
        System.arraycopy(encrypted, 0, packed, iv.length, encrypted.length);
        return "enc:" + Base64.encodeToString(packed, Base64.NO_WRAP);
    }

    private String decryptToken(String stored) throws Exception {
        if (!stored.startsWith("enc:")) return stored;
        byte[] packed = Base64.decode(stored.substring(4), Base64.NO_WRAP);
        if (packed.length <= 12) throw new IllegalStateException("Nieprawidłowy zaszyfrowany token.");
        byte[] iv = java.util.Arrays.copyOfRange(packed, 0, 12);
        byte[] encrypted = java.util.Arrays.copyOfRange(packed, 12, packed.length);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, getOrCreateKey(), new GCMParameterSpec(128, iv));
        return new String(cipher.doFinal(encrypted), StandardCharsets.UTF_8);
    }

    private String readToken() {
        String stored = prefs.getString("token_enc", "");
        if (!stored.isEmpty()) {
            try { return decryptToken(stored); }
            catch (Exception ex) { return ""; }
        }
        // One-time migration from the pre-Keystore local preference key.
        String legacy = prefs.getString("token", "");
        if (!legacy.isEmpty()) {
            try {
                prefs.edit().putString("token_enc", encryptToken(legacy)).remove("token").apply();
                return legacy;
            } catch (Exception ex) { return ""; }
        }
        return "";
    }

    private void loadReport() {
        String base = prefs.getString("url", "");
        String token = readToken();
        if (base.isEmpty() || token.isEmpty()) { status.setText("Najpierw skonfiguruj backend."); return; }
        status.setText("Pobieranie raportu…");
        reportView.setText("");
        io.execute(() -> {
            HttpURLConnection c = null;
            try {
                URL endpoint = new URL(base + "/api/robotics/report");
                c = (HttpURLConnection) endpoint.openConnection();
                c.setRequestMethod("GET");
                c.setConnectTimeout(12000);
                c.setReadTimeout(20000);
                c.setRequestProperty("Accept", "application/json");
                c.setRequestProperty("Authorization", "Bearer " + token);
                int code = c.getResponseCode();
                java.io.InputStream stream = code >= 200 && code < 300 ? c.getInputStream() : c.getErrorStream();
                byte[] bytes = stream == null ? new byte[0] : stream.readNBytes(1_500_001);
                if (bytes.length > 1_500_000) throw new IllegalStateException("Raport przekracza limit 1,5 MB.");
                String body = new String(bytes, StandardCharsets.UTF_8);
                if (code != 200) throw new IllegalStateException("Backend HTTP " + code + ": " + body);
                JSONObject report = new JSONObject(body);
                String validation = validate(report);
                if (validation != null) throw new IllegalStateException(validation);
                String summary = summarize(report);
                runOnUiThread(() -> { status.setText("Raport poprawny • " + report.optString("strategy_version")); reportView.setText(summary); });
            } catch (Exception e) {
                String msg = e.getMessage() == null ? e.getClass().getSimpleName() : e.getMessage();
                runOnUiThread(() -> status.setText("Raport niedostępny: " + msg));
            } finally { if (c != null) c.disconnect(); }
        });
    }

    private String validate(JSONObject r) {
        if (!r.optBoolean("release_ready", false)) return "Raport nie ma release_ready=true.";
        String strategy = r.optString("strategy_version", r.optString("strategy", ""));
        if (!"balanced-1.3-audit".equals(strategy)) return "Nieobsługiwana strategia: " + strategy;
        String stamp = first(r, "generated_at", "generated_at_utc", "created_at", "as_of");
        if (stamp.isEmpty()) return "Brak znacznika czasu raportu.";
        try {
            Instant generated = Instant.parse(stamp);
            Duration age = Duration.between(generated, Instant.now());
            if (age.isNegative() || age.toHours() > 36) return "Raport jest przyszły lub starszy niż 36 godzin.";
        } catch (Exception ex) { return "Nieprawidłowy znacznik czasu raportu."; }
        return null;
    }

    private String first(JSONObject o, String... keys) {
        for (String k : keys) { String v = o.optString(k, ""); if (!v.isEmpty() && !"null".equals(v)) return v; }
        return "";
    }

    private String summarize(JSONObject r) {
        StringBuilder b = new StringBuilder();
        b.append("Wygenerowano: ").append(first(r,"generated_at","generated_at_utc","created_at","as_of")).append("\n");
        b.append("Strategia: ").append(r.optString("strategy_version", r.optString("strategy",""))).append("\n");
        b.append("Status publikacji: release_ready=true\n\n");
        JSONArray keys = r.names();
        if (keys != null) for (int i=0; i<keys.length(); i++) {
            String k = keys.optString(i);
            if ("release_ready".equals(k) || "strategy_version".equals(k) || "strategy".equals(k)) continue;
            Object v = r.opt(k);
            String text = String.valueOf(v);
            if (text.length() > 7000) text = text.substring(0,7000) + "…";
            b.append(k).append(": ").append(text).append("\n\n");
        }
        return b.toString();
    }

    @Override protected void onDestroy() { super.onDestroy(); io.shutdownNow(); }
}
