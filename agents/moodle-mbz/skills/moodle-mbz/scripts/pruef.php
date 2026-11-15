<?php
// Prüft einen (wiederhergestellten) Kurs gegen kursplan.json.
// Aufruf: php pruef.php <kursid> [abschnitt-id|alle] [abschnittsnummer]   (Standard alle)
// Mit abschnittsnummer wird der Abschnitt über seine Nummer gesucht (Einfügen in bestehenden Kurs: der Name des Zielabschnitts bleibt erhalten).
// Gibt für jede Abweichung eine Zeile "FEHLER ..." aus und am Ende "Fehler gesamt: N".
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->libdir . '/gradelib.php');
require_once(__DIR__ . '/plan.php');
global $DB;

$kursid = (int) ($argv[1] ?? 0);
$wahl = $argv[2] ?? 'alle';
$nummer = (int) ($argv[3] ?? 0);
$planpfad = getenv('MBZ_PLAN') ?: '/work/export/kursplan.json';
$base = rtrim(dirname($planpfad), '/') . '/';
$plan = mbz_plan_laden($planpfad);
$course = $DB->get_record('course', ['id' => $kursid], '*', MUST_EXIST);
$mods = get_fast_modinfo($course);
$fehler = 0;
function fehler($msg) { global $fehler; $fehler++; echo "FEHLER $msg\n"; }
function lf($s) { return str_replace(["\r\n", "\r"], "\n", $s); }
function hatcr($s) { return strpos((string) $s, "\r") !== false; }

echo "Kurs: {$course->fullname} ({$course->shortname}), Format {$course->format}\n";
$abschnitte = $plan['abschnitte'];
if ($wahl !== 'alle') {
    $abschnitte = array_values(array_filter($abschnitte, fn($a) => $a['id'] === $wahl));
    if (!$abschnitte) { fehler("Abschnitt $wahl nicht im Plan"); }
}
// Zeilen course_sections des Kurses nach Namen; bei mehreren Treffern die letzte (beim Einfügen in einen bestehenden Kurs hinten angehängt)
$zeilen = $DB->get_records('course_sections', ['course' => $kursid], 'section');
$gesamt = 0;
$namen = []; foreach ($plan['abschnitte'] as $x) { foreach ($x['aktivitaeten'] ?? [] as $y) { $namen[$y['id']] = $y['name']; } }
foreach ($abschnitte as $ab) {
    $sec = null;
    foreach ($zeilen as $z) { if ($nummer > 0 ? (int) $z->section === $nummer : (string) $z->name === $ab['name']) { $sec = $z; } }
    if (!$sec) { fehler("Abschnitt '{$ab['name']}' fehlt im Kurs" . ($nummer > 0 ? " (Nummer $nummer)" : '')); continue; }
    echo "Abschnitt {$sec->section}: '{$sec->name}'\n";
    if (hatcr($sec->summary)) { fehler("CR in Abschnittstext '{$ab['name']}'"); }
    $seq = array_values(array_filter(explode(',', (string) $sec->sequence)));
    $soll = $ab['aktivitaeten'] ?? [];
    if (count($seq) !== count($soll)) { fehler("Abschnitt '{$ab['name']}': " . count($seq) . " Aktivitäten, Plan " . count($soll)); }
    foreach ($soll as $pos => $a) {
        $gesamt++;
        $cm = isset($seq[$pos]) ? $mods->get_cm($seq[$pos]) : null;
        $e = $a['einstellungen'] ?? [];
        $probleme = [];
        $extra = '';
        $erwart = ['label' => 'label', 'page' => 'page', 'url' => 'url', 'assign' => 'assign', 'quiz' => 'quiz', 'file' => 'resource', 'workshop' => 'workshop'][$a['art']] ?? '?';
        if (!$cm) { $probleme[] = 'fehlt'; }
        else {
            if ($cm->modname !== $erwart) { $probleme[] = "Typ {$cm->modname} statt $erwart"; }
            if ((bool) $cm->visible !== !empty($a['sichtbar'])) { $probleme[] = 'Sichtbarkeit'; }
            if ($a['art'] !== 'label' && $cm->name !== $a['name']) { $probleme[] = "Name '{$cm->name}'"; }
            $tab = $cm->modname === 'resource' ? 'resource' : $cm->modname;
            if ($a['art'] !== 'label') {
                $intro = $DB->get_field($tab, 'intro', ['id' => $cm->instance]);
                if (hatcr($intro)) { $probleme[] = 'CR in Beschreibung'; }
                if (!empty($a['beschreibung'])) {
                    $s = lf(file_get_contents($base . $a['beschreibung']));
                    if (strpos($s, '{{LINK:') === false && strlen($intro) !== strlen($s)) { $probleme[] = 'Beschreibung ' . strlen($intro) . '/' . strlen($s) . ' Zeichen'; }
                }
            }
            $abz = ['keiner' => 0, 'manuell' => 1, 'ansicht' => 2, 'abgabe' => 2][$a['abschluss'] ?? 'keiner'] ?? -1;
            if ((int) $cm->completion !== $abz) { $probleme[] = 'Abschluss ' . $cm->completion . ' statt ' . $abz; }
            if (!empty($a['voraussetzung'])) {
                $av = json_decode((string) $cm->availability, true);
                $ist = []; foreach ($av['c'] ?? [] as $c) { if (($c['type'] ?? '') === 'completion') { $ist[] = $mods->get_cm($c['cm'])->name; } }
                $soll_v = []; foreach ($a['voraussetzung'] as $vid) { $soll_v[] = $namen[$vid] ?? '?'; }
                sort($ist); sort($soll_v);
                if ($ist !== $soll_v) { $probleme[] = 'Voraussetzung ' . implode(' | ', $ist) . ' statt ' . implode(' | ', $soll_v); }
            } elseif ($cm->availability) { $probleme[] = 'unerwartete Zugriffsbeschränkung'; }
            if ($a['art'] === 'label') {
                $inh = $DB->get_field('label', 'intro', ['id' => $cm->instance]);
                if (hatcr($inh)) { $probleme[] = 'CR im Text'; }
                if (strlen($inh) !== strlen(lf(file_get_contents($base . $a['quelle'])))) { $probleme[] = 'Länge'; }
            }
            if ($a['art'] === 'page') {
                $inh = $DB->get_field('page', 'content', ['id' => $cm->instance]);
                $s = lf(file_get_contents($base . $a['quelle']));
                // Link-Platzhalter ändern die Länge: nur vergleichen, wenn keiner vorkommt
                $extra = ' Inhalt ' . strlen($inh);
                if (hatcr($inh)) { $probleme[] = 'CR im Inhalt'; }
                if (strpos($s, '{{LINK:') === false && strlen($inh) !== strlen($s)) { $probleme[] = 'Länge ' . strlen($inh) . '/' . strlen($s); }
            }
            if ($a['art'] === 'url') {
                $u = $DB->get_field('url', 'externalurl', ['id' => $cm->instance]);
                if ($u !== $e['url']) { $probleme[] = "URL $u"; }
            }
            if ($a['art'] === 'quiz') {
                $n = $DB->count_records('quiz_slots', ['quizid' => $cm->instance]);
                $erwartet = preg_match_all('/<question\s+type="(?!category)/', lf(file_get_contents($base . $a['quelle'])));
                $extra = " Slots $n";
                if ($n !== $erwartet) { $probleme[] = "Slots $n, Quelle $erwartet"; }
                $t = $DB->get_field('quiz', 'timelimit', ['id' => $cm->instance]);
                if (isset($e['zeitlimit_min']) && (int) $t !== (int) $e['zeitlimit_min'] * 60) { $probleme[] = 'Zeitlimit'; }
                $qz = $DB->get_record('quiz', ['id' => $cm->instance], 'preferredbehaviour,grade,attempts');
                if ($qz->preferredbehaviour !== ($e['verhalten'] ?? 'deferredfeedback')) { $probleme[] = 'Verhalten ' . $qz->preferredbehaviour; }
                if ((float) $qz->grade !== (float) ($e['bewertung_punkte'] ?? 100)) { $probleme[] = 'Bewertung ' . $qz->grade; }
            }
            if ($a['art'] === 'assign') {
                $ft = $DB->get_field('assign_plugin_config', 'value', ['assignment' => $cm->instance, 'plugin' => 'file', 'subtype' => 'assignsubmission', 'name' => 'filetypeslist']);
                $extra = " Dateitypen=$ft";
                if (isset($e['erlaubte_dateitypen']) && (string) $ft !== implode(';', $e['erlaubte_dateitypen'])) { $probleme[] = 'Dateitypen'; }
            }
            if ($a['art'] === 'workshop') {
                $w = $DB->get_record('workshop', ['id' => $cm->instance], '*', MUST_EXIST);
                $ctxw = context_module::instance($cm->id)->id;
                foreach (['instructauthors' => ['anleitung_autoren', 'dateien_autoren'], 'instructreviewers' => ['anleitung_gutachter', 'dateien_gutachter']] as $feld => [$qk, $dk]) {
                    if (hatcr($w->$feld)) { $probleme[] = "CR in $feld"; }
                    if (!empty($a[$qk]) && strlen($w->$feld) !== strlen(lf(file_get_contents($base . $a[$qk])))) { $probleme[] = "$feld Länge"; }
                    $n = count(get_file_storage()->get_area_files($ctxw, 'mod_workshop', $feld, 0, 'id', false));
                    if ($n !== count($a[$dk] ?? [])) { $probleme[] = "Dateien $feld: $n statt " . count($a[$dk] ?? []); }
                }
                $nk = $DB->count_records('workshopform_accumulative', ['workshopid' => $w->id]);
                $extra = " Kriterien $nk, Punkte " . (float) $w->grade . '/' . (float) $w->gradinggrade;
                if ($nk !== count($e['kriterien'] ?? [])) { $probleme[] = "Kriterien $nk"; }
                if ((float) $w->grade !== (float) ($e['punkte_abgabe'] ?? 80) || (float) $w->gradinggrade !== (float) ($e['punkte_beurteilung'] ?? 20)) { $probleme[] = 'Punkte'; }
            }
            if ($a['art'] === 'file') {
                $files = get_file_storage()->get_area_files(context_module::instance($cm->id)->id, 'mod_resource', 'content', 0, 'id', false);
                $extra = ' Dateien ' . implode(',', array_map(fn($f) => $f->get_filename() . '(' . $f->get_filesize() . ')', $files));
                if (count($files) !== 1) { $probleme[] = 'Dateianzahl ' . count($files); }
                elseif ($files ? (int) reset($files)->get_filesize() !== filesize($base . $a['quelle']) : false) { $probleme[] = 'Dateigröße'; }
            }
        }
        if ($probleme) { fehler("{$a['id']}: " . implode('; ', $probleme)); }
        else { echo sprintf("OK    %-7s %s%s\n", $a['art'], $a['name'], $extra); }
    }
}
echo "Aktivitäten geprüft: $gesamt\n";

// Bewertung (nur bei ganzem Kurs sinnvoll)
if ($wahl === 'alle' && !empty($plan['bewertung'])) {
    $b = $plan['bewertung'];
    $kk = grade_category::fetch_course_category($kursid);
    echo "Bewertung: Kurs-Aggregation {$kk->aggregation} (10 = gewichteter Mittelwert)\n";
    if ((int) $kk->aggregation !== 10) { fehler('Kurs-Aggregation nicht gewichteter Mittelwert'); }
    foreach ($b['kategorien'] ?? [] as $k) {
        $c = null;
        foreach (grade_category::fetch_all(['courseid' => $kursid]) as $x) { if ($x->fullname === $k['name']) { $c = $x; } }
        if (!$c) { fehler("Kategorie '{$k['name']}' fehlt"); continue; }
        $coef = (float) $c->get_grade_item()->aggregationcoef;
        $n = count(grade_item::fetch_all(['courseid' => $kursid, 'categoryid' => $c->id]));
        echo "Kategorie '{$c->fullname}': Gewicht $coef, Elemente $n\n";
        if (abs($coef - (float) $k['gewicht_prozent']) > 0.001) { fehler("Gewicht Kategorie '{$k['name']}'"); }
        if ($n !== count($k['aktivitaeten'])) { fehler("Elemente Kategorie '{$k['name']}': $n statt " . count($k['aktivitaeten'])); }
    }
    foreach ($plan['abschnitte'] as $ab) {
        foreach ($ab['aktivitaeten'] ?? [] as $a) {
            if (!isset($b['gewichte'][$a['id']])) { continue; }
            $zeile = null;
            foreach ($mods->get_cms() as $cm) { if ($cm->name === $a['name'] && in_array($cm->modname, ['quiz', 'assign', 'page', 'resource', 'url'])) { $zeile = $cm; } }
            if (!$zeile) { fehler("Bewertungselement {$a['id']} nicht gefunden"); continue; }
            $g = grade_item::fetch(['courseid' => $kursid, 'itemtype' => 'mod', 'itemmodule' => $zeile->modname, 'iteminstance' => $zeile->instance, 'itemnumber' => 0]);
            if (!$g || abs((float) $g->aggregationcoef - (float) $b['gewichte'][$a['id']]) > 0.001) { fehler("Gewicht {$a['id']}"); }
        }
    }
    if (!empty($b['notenskala']['stufen'])) {
        $buch = $DB->get_records('grade_letters', ['contextid' => context_course::instance($kursid)->id], 'lowerboundary DESC');
        echo 'Notenskala: ' . implode(', ', array_map(fn($l) => $l->lowerboundary . '=' . $l->letter, $buch)) . "\n";
        if (count($buch) !== count($b['notenskala']['stufen'])) { fehler('Notenskala: Anzahl der Stufen'); }
    }
}
$nfragen = $DB->count_records_sql("SELECT COUNT(*) FROM {question} q JOIN {question_versions} qv ON qv.questionid=q.id JOIN {question_bank_entries} qbe ON qbe.id=qv.questionbankentryid JOIN {question_categories} qc ON qc.id=qbe.questioncategoryid JOIN {context} ctx ON ctx.id=qc.contextid WHERE q.parent = 0 AND ctx.instanceid = ? AND ctx.contextlevel = 50", [$kursid]);
echo "Fragen im Kurs: $nfragen\n";
if ($wahl === 'alle') {
    $erw = 0;
    foreach ($plan['kurs']['fragensammlung'] ?? [] as $f) { $erw += preg_match_all('/<question\s+type="(?!category)/', lf(file_get_contents($base . $f))); }
    foreach ($plan['abschnitte'] as $x) { foreach ($x['aktivitaeten'] ?? [] as $y) { if ($y['art'] === 'quiz') { $erw += preg_match_all('/<question\s+type="(?!category)/', lf(file_get_contents($base . $y['quelle']))); } } }
    if ($nfragen !== $erw) { fehler("Fragen im Kurs $nfragen, laut Quellen $erw"); }
}
echo "Fehler gesamt: $fehler\n";

