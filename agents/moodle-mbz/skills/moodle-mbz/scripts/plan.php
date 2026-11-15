<?php
// Lädt kursplan.json. Version 2 (abschnitte[]) wird geprüft, Version 1 (ein Abschnitt, aktivitaeten[]) umgewandelt.
// Wird von bau.php und pruef.php verwendet.

function mbz_plan_laden($pfad) {
    $roh = file_get_contents($pfad);
    if ($roh === false) { fwrite(STDERR, "Kursplan fehlt: $pfad\n"); exit(1); }
    $plan = json_decode($roh, true);
    if (!is_array($plan)) { fwrite(STDERR, "Kursplan ist kein gültiges JSON: " . json_last_error_msg() . "\n"); exit(1); }

    if (!isset($plan['abschnitte']) && isset($plan['aktivitaeten'])) { // Version 1
        $b = $plan['bewertung'] ?? null;
        $plan['kurs']['kurzname'] = $plan['kurs']['kurzname'] ?? 'MBZ-BAU';
        $plan['kurs']['zusammenfassung'] = $plan['kurs']['zusammenfassung'] ?? '<p>' . ($plan['kurs']['name'] ?? '') . '</p>';
        $plan['abschnitte'] = [[
            'id' => 'abschnitt',
            'name' => $plan['abschnitt']['name'],
            'zusammenfassung' => '<p>' . ($plan['abschnitt']['zusammenfassung'] ?? '') . '</p>',
            'aktivitaeten' => $plan['aktivitaeten'],
        ]];
        if ($b) {
            $assigns = [];
            foreach ($plan['aktivitaeten'] as $a) { if ($a['art'] === 'assign') { $assigns[] = $a['id']; } }
            $plan['bewertung'] = [
                'kategorien' => [['name' => $b['abgaben']['kategorie'], 'gewicht_prozent' => $b['abgaben']['gewicht_prozent'], 'aktivitaeten' => $assigns]],
                'gewichte' => $b['tests'] ?? [],
                'notenskala' => $b['notenskala'] ?? [],
            ];
        }
        unset($plan['aktivitaeten'], $plan['abschnitt']);
    }

    // Prüfung
    foreach (['kurs.name', 'kurs.kurzname'] as $pf) {
        [$a, $k] = explode('.', $pf);
        if (empty($plan[$a][$k])) { fwrite(STDERR, "Plan: $pf fehlt\n"); exit(1); }
    }
    if (empty($plan['abschnitte'])) { fwrite(STDERR, "Plan: abschnitte fehlt oder leer\n"); exit(1); }
    $ids = [];
    foreach ($plan['abschnitte'] as $ab) {
        foreach (['id', 'name'] as $f) { if (empty($ab[$f])) { fwrite(STDERR, "Plan: Abschnitt ohne $f\n"); exit(1); } }
        if (isset($ids['A:' . $ab['id']])) { fwrite(STDERR, "Plan: Abschnitts-id doppelt: {$ab['id']}\n"); exit(1); }
        if (!preg_match('/^[A-Za-z0-9_-]+$/', $ab['id'])) { fwrite(STDERR, "Plan: Abschnitts-id nur A-Z a-z 0-9 _ - erlaubt: {$ab['id']}\n"); exit(1); }
        $ids['A:' . $ab['id']] = true;
        foreach ($ab['aktivitaeten'] ?? [] as $a) {
            foreach (['id', 'art', 'name'] as $f) { if (empty($a[$f])) { fwrite(STDERR, "Plan: Aktivität ohne $f im Abschnitt {$ab['id']}\n"); exit(1); } }
            if (isset($ids[$a['id']])) { fwrite(STDERR, "Plan: Aktivitäts-id doppelt: {$a['id']}\n"); exit(1); }
            $ids[$a['id']] = true;
        }
    }
    return $plan;
}

