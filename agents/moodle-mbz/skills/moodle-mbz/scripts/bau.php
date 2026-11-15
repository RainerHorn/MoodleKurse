<?php
// Baut einen Kurs aus kursplan.json (Version 2, Version 1 wird umgewandelt) mit Moodles eigener API
// und sichert ihn als .mbz: ganzer Kurs ODER einzelne Abschnitte (ohne Nutzer, Anmeldungen, Protokolle).
//
// Umgebungsvariablen:
//   MBZ_PLAN      Pfad zur kursplan.json            (Standard /work/export/kursplan.json)
//   MBZ_MODUS     kurs | abschnitt                  (Standard kurs)
//   MBZ_ABSCHNITT Abschnitts-id oder "alle"         (nur bei MBZ_MODUS=abschnitt)
//   MBZ_ZIELNUMMER Nur bei einem einzelnen Abschnitt: Abschnittsnummer, die der Abschnitt im Zielkurs haben soll.
//                 Beim Einfügen in einen bestehenden Kurs landen die Aktivitäten im gleichnummerierten Abschnitt des Zielkurses.
//                 Dann wird nur dieser Abschnitt gebaut (ohne Bewertungsstruktur, Links auf andere Abschnitte sind nicht möglich).
//   KURSKURZ      Kurzname des Baukurses            (Standard: kurs.kurzname aus dem Plan)
//   MBZ_OUT       Ausgabeordner                     (Standard /work/out)
//
// Zeilenenden: Alle Quelldateien werden beim Einlesen auf LF normalisiert (CRLF und einzelnes CR -> LF).
// Die eigentliche Normalisierung der Dateien übernimmt scripts/eol.py; das hier ist die zweite Absicherung.
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->dirroot . '/course/modlib.php');
require_once($CFG->libdir . '/filelib.php');
require_once($CFG->libdir . '/resourcelib.php');
require_once($CFG->libdir . '/gradelib.php');
require_once($CFG->dirroot . '/question/format.php');
require_once($CFG->dirroot . '/question/format/xml/format.php');
require_once($CFG->dirroot . '/mod/quiz/locallib.php');
require_once($CFG->dirroot . '/backup/util/includes/backup_includes.php');
require_once(__DIR__ . '/plan.php');

\core\session\manager::set_user(get_admin());
global $USER, $DB;

$planpfad = getenv('MBZ_PLAN') ?: '/work/export/kursplan.json';
$base = rtrim(dirname($planpfad), '/') . '/';
$plan = mbz_plan_laden($planpfad);
$modus = getenv('MBZ_MODUS') ?: 'kurs';
$wahl = getenv('MBZ_ABSCHNITT') ?: '';
$zielnr = (int) (getenv('MBZ_ZIELNUMMER') ?: 0);
if ($zielnr > 0) {
    if ($modus !== 'abschnitt' || $wahl === 'alle') { fwrite(STDERR, "MBZ_ZIELNUMMER nur mit einem einzelnen Abschnitt (MBZ_MODUS=abschnitt, MBZ_ABSCHNITT=<id>)\n"); exit(1); }
    $plan['abschnitte'] = array_values(array_filter($plan['abschnitte'], fn($a) => $a['id'] === $wahl));
    if (!$plan['abschnitte']) { fwrite(STDERR, "Abschnitt unbekannt: $wahl\n"); exit(1); }
    $plan['bewertung'] = null;
}
$nummer = []; // Abschnitts-id => Abschnittsnummer im gebauten Kurs
foreach ($plan['abschnitte'] as $i => $ab) { $nummer[$ab['id']] = $zielnr > 0 ? $zielnr : $i + 1; }
$kurzname = getenv('KURSKURZ') ?: $plan['kurs']['kurzname'];
$ausgabe = rtrim(getenv('MBZ_OUT') ?: '/work/out', '/') . '/';
if (!is_dir($ausgabe)) { mkdir($ausgabe, 0777, true); }
if (!in_array($modus, ['kurs', 'abschnitt'], true)) { fwrite(STDERR, "MBZ_MODUS muss kurs oder abschnitt sein\n"); exit(1); }
if ($modus === 'abschnitt' && $wahl === '') { fwrite(STDERR, "Bei MBZ_MODUS=abschnitt ist MBZ_ABSCHNITT (id oder alle) nötig\n"); exit(1); }

function text($pfad) {
    global $base;
    $inhalt = file_get_contents($base . $pfad);
    if ($inhalt === false) { fwrite(STDERR, "Datei fehlt: $pfad\n"); exit(1); }
    if (substr($inhalt, 0, 3) === "\xEF\xBB\xBF") { $inhalt = substr($inhalt, 3); }
    return str_replace(["\r\n", "\r"], "\n", $inhalt);
}

// ---------- Kurs ----------
if ($alt = $DB->get_record('course', ['shortname' => $kurzname])) { delete_course($alt, false); }
$d = new stdClass();
$d->fullname = $plan['kurs']['name'];
$d->shortname = $kurzname;
$d->category = 1;
$d->format = $plan['kurs']['format'] ?? 'topics';
$d->summary = $plan['kurs']['zusammenfassung'] ?? '';
$d->summaryformat = FORMAT_HTML;
$d->visible = 1;
$d->startdate = time();
$braucht_abschluss = false;
foreach ($plan['abschnitte'] as $ab) { foreach ($ab['aktivitaeten'] ?? [] as $a) { if (($a['abschluss'] ?? 'keiner') !== 'keiner') { $braucht_abschluss = true; } } }
$d->enablecompletion = $braucht_abschluss ? 1 : 0;
$course = create_course($d);
$context = context_course::instance($course->id);
// Das automatisch angelegte Ankündigungsforum gehört nicht in die Sicherung
foreach (get_fast_modinfo($course)->get_cms() as $cmi) {
    if ($cmi->modname === 'forum') { course_delete_module($cmi->id); }
}
$anzahl = count($plan['abschnitte']);
course_create_sections_if_missing($course, range(1, max($nummer)));
$abschnittid = []; // plan-id => Zeile course_sections
foreach ($plan['abschnitte'] as $i => $ab) {
    $sec = $DB->get_record('course_sections', ['course' => $course->id, 'section' => $nummer[$ab['id']]], '*', MUST_EXIST);
    $sum = isset($ab['zusammenfassung_datei']) ? text($ab['zusammenfassung_datei']) : ($ab['zusammenfassung'] ?? '');
    course_update_section($course, $sec, ['name' => $ab['name'], 'summary' => str_replace(["\r\n", "\r"], "\n", $sum), 'summaryformat' => FORMAT_HTML]);
    $abschnittid[$ab['id']] = $sec->id;
}
echo "Kurs {$course->id} angelegt, $anzahl Abschnitt(e)\n";

// ---------- Fragen importieren ----------
question_make_default_categories([$context]);
$fragen = []; // aktivitäts-id => [questionids]
function fragen_importieren($datei, $course, $context) {
    $qformat = new qformat_xml();
    $qformat->setCategory(question_get_default_category($context->id));
    $qformat->setContexts([$context]);
    $qformat->setCourse($course);
    $qformat->setFilename($datei);
    $qformat->setRealfilename(basename($datei));
    $qformat->setMatchgrades('error');
    $qformat->setCatfromfile(true);
    $qformat->setContextfromfile(false);
    $qformat->setStoponerror(true);
    ob_start();
    if (!$qformat->importpreprocess()) { ob_end_clean(); fwrite(STDERR, "Import vorbereiten fehlgeschlagen: $datei\n"); exit(1); }
    if (!$qformat->importprocess()) { $msg = ob_get_clean(); fwrite(STDERR, "Import fehlgeschlagen: $datei\n$msg\n"); exit(1); }
    $qformat->importpostprocess();
    ob_end_clean();
    return $qformat->questionids;
}
foreach ($plan['kurs']['fragensammlung'] ?? [] as $datei) {
    $ids = fragen_importieren($base . $datei, $course, $context);
    echo "Fragensammlung $datei: " . count($ids) . "\n";
}
foreach ($plan['abschnitte'] as $ab) {
    foreach ($ab['aktivitaeten'] as $a) {
        if ($a['art'] !== 'quiz') { continue; }
        $fragen[$a['id']] = fragen_importieren($base . $a['quelle'], $course, $context);
        echo "Fragen importiert {$a['id']}: " . count($fragen[$a['id']]) . "\n";
    }
}

// ---------- Aktivitäten ----------
// Abschluss: keiner | ansicht (Aktivität ansehen) | abgabe (nur Aufgabe: Abgabe) | manuell
function abschlussparams($a) {
    $z = $a['abschluss'] ?? 'keiner';
    switch ($z) {
        case 'keiner': return ['completion' => 0];
        case 'manuell': return ['completion' => 1];
        case 'ansicht': return ['completion' => 2, 'completionview' => 1];
        case 'abgabe':
            if (($a['art'] ?? '') !== 'assign') { fwrite(STDERR, "abschluss=abgabe nur bei assign ($a[id])\n"); exit(1); }
            return ['completion' => 2, 'completionview' => 0, 'completionsubmit' => 1];
    }
    fwrite(STDERR, "Unbekannter Abschluss '$z' bei $a[id] (keiner, ansicht, abgabe, manuell)\n"); exit(1);
}
function modul($course, $name, array $p, $abschnittnr) {
    global $DB, $aktuell;
    $p = array_merge($p, abschlussparams($aktuell));
    $mi = (object) array_merge([
        'modulename' => $name, 'module' => $DB->get_field('modules', 'id', ['name' => $name], MUST_EXIST),
        'course' => $course->id, 'section' => $abschnittnr, 'visible' => 1, 'visibleoncoursepage' => 1,
        'cmidnumber' => '', 'groupmode' => 0, 'groupingid' => 0, 'availabilityconditionsjson' => '', 'completion' => 0,
    ], $p);
    return add_moduleinfo($mi, $course);
}
$cm = [];      // aktivitäts-id => cmid
$instanz = []; // aktivitäts-id => [art, instanz]
$alle = [];    // aktivitäts-id => Plan-Eintrag
$sektion = []; // aktivitäts-id => Abschnitts-id
foreach ($plan['abschnitte'] as $i => $ab) {
    $nr = $nummer[$ab['id']];
    foreach ($ab['aktivitaeten'] as $a) {
        $alle[$a['id']] = $a;
        $sektion[$a['id']] = $ab['id'];
        $intro = !empty($a['beschreibung']) ? text($a['beschreibung']) : '';
        $zeige = !empty($a['beschreibung_anzeigen']) ? 1 : 0;
        $sichtbar = !empty($a['sichtbar']) ? 1 : 0;
        $e = $a['einstellungen'] ?? [];
        $aktuell = $a;
        switch ($a['art']) {
            case 'label':
                $r = modul($course, 'label', ['name' => $a['name'], 'intro' => text($a['quelle']), 'introformat' => FORMAT_HTML, 'visible' => $sichtbar], $nr);
                break;
            case 'page':
                $r = modul($course, 'page', ['name' => $a['name'], 'intro' => $intro, 'introformat' => FORMAT_HTML, 'showdescription' => $zeige, 'visible' => $sichtbar,
                    'content' => text($a['quelle']), 'contentformat' => FORMAT_HTML, 'display' => RESOURCELIB_DISPLAY_OPEN,
                    'printintro' => 0, 'printlastmodified' => 0], $nr);
                break;
            case 'url':
                $r = modul($course, 'url', ['name' => $a['name'], 'intro' => $intro, 'introformat' => FORMAT_HTML, 'showdescription' => $zeige, 'visible' => $sichtbar,
                    'externalurl' => $e['url'], 'display' => RESOURCELIB_DISPLAY_AUTO], $nr);
                break;
            case 'file':
                $uctx = context_user::instance($USER->id);
                $draft = file_get_unused_draft_itemid();
                get_file_storage()->create_file_from_pathname(['contextid' => $uctx->id, 'component' => 'user', 'filearea' => 'draft', 'itemid' => $draft,
                    'filepath' => '/', 'filename' => basename($a['quelle'])], $base . $a['quelle']);
                $r = modul($course, 'resource', ['name' => $a['name'], 'intro' => $intro, 'introformat' => FORMAT_HTML, 'showdescription' => $zeige, 'visible' => $sichtbar,
                    'files' => $draft, 'display' => RESOURCELIB_DISPLAY_AUTO, 'showsize' => 1, 'showtype' => 1, 'showdate' => 0, 'printintro' => 1], $nr);
                break;
            case 'assign':
                $r = modul($course, 'assign', [
                    'name' => $a['name'], 'intro' => $intro, 'introformat' => FORMAT_HTML, 'showdescription' => $zeige, 'visible' => $sichtbar,
                    'alwaysshowdescription' => 1, 'submissiondrafts' => 0, 'requiresubmissionstatement' => 0, 'sendnotifications' => 0, 'sendlatenotifications' => 0,
                    'sendstudentnotifications' => 1, 'duedate' => 0, 'allowsubmissionsfromdate' => 0, 'cutoffdate' => 0, 'gradingduedate' => 0,
                    'grade' => $e['punkte'] ?? 100, 'teamsubmission' => 0, 'requireallteammemberssubmit' => 0, 'blindmarking' => 0, 'hidegrader' => 0,
                    'markingworkflow' => 0, 'markingallocation' => 0, 'attemptreopenmethod' => 'none', 'maxattempts' => -1,
                    'preventsubmissionnotingroup' => 0, 'timelimit' => 0,
                    'assignsubmission_file_enabled' => 1, 'assignsubmission_file_maxfiles' => $e['max_dateien'] ?? 3,
                    'assignsubmission_file_maxsizebytes' => ($e['max_groesse_mb'] ?? 10) * 1024 * 1024,
                    'assignsubmission_file_filetypes' => implode(';', $e['erlaubte_dateitypen'] ?? []),
                    'assignsubmission_onlinetext_enabled' => !empty($e['online_text']) ? 1 : 0,
                    'assignfeedback_comments_enabled' => 1, 'assignfeedback_comments_commentinline' => 0,
                    'assignfeedback_file_enabled' => 1, 'assignfeedback_editpdf_enabled' => 0,
                ], $nr);
                break;
            case 'quiz':
                $opt = [];
                foreach (['attempt', 'correctness', 'marks', 'specificfeedback', 'generalfeedback', 'rightanswer', 'overallfeedback'] as $f) {
                    $opt[$f . 'during'] = ($f === 'attempt') ? 1 : 0;
                    foreach (['immediately', 'open', 'closed'] as $w) { $opt[$f . $w] = 1; }
                }
                $r = modul($course, 'quiz', array_merge([
                    'name' => $a['name'], 'intro' => $intro, 'introformat' => FORMAT_HTML, 'showdescription' => $zeige, 'visible' => $sichtbar,
                    'timeopen' => 0, 'timeclose' => 0, 'timelimit' => ($e['zeitlimit_min'] ?? 0) * 60, 'overduehandling' => 'autosubmit', 'graceperiod' => 0,
                    'preferredbehaviour' => $e['verhalten'] ?? 'deferredfeedback', 'canredoquestions' => 0, 'attempts' => $e['versuche'] ?? 0, 'attemptonlast' => 0,
                    'grademethod' => QUIZ_GRADEHIGHEST, 'decimalpoints' => 2, 'questiondecimalpoints' => -1, 'questionsperpage' => 5, 'navmethod' => 'free',
                    'shuffleanswers' => !empty($e['antworten_mischen']) ? 1 : 0, 'sumgrades' => 0, 'grade' => $e['bewertung_punkte'] ?? 100, 'browsersecurity' => '-', 'delay1' => 0, 'delay2' => 0,
                    'showuserpicture' => 0, 'showblocks' => 0, 'quizpassword' => '', 'subnet' => '',
                    'feedbacktext' => [['text' => '', 'format' => FORMAT_HTML, 'itemid' => 0]], 'feedbackboundaries' => [], 'feedbackboundarycount' => -1,
                ], $opt), $nr);
                break;
            case 'workshop':
                // Peer-Review-Workshop (Bewertungsstrategie "Punkte pro Kriterium" = accumulative). Beginnt in der Vorbereitungsphase.
                if (($e['strategie'] ?? 'accumulative') !== 'accumulative') { fwrite(STDERR, "Workshop {$a['id']}: nur strategie accumulative wird unterstützt\n"); exit(1); }
                $uctx = context_user::instance($USER->id);
                $editor = function ($datei, array $dateien) use ($uctx) {
                    $item = file_get_unused_draft_itemid();
                    foreach ($dateien as $pfad) {
                        get_file_storage()->create_file_from_pathname(['contextid' => $uctx->id, 'component' => 'user', 'filearea' => 'draft', 'itemid' => $item,
                            'filepath' => '/', 'filename' => basename($pfad)], $GLOBALS['base'] . $pfad);
                    }
                    return ['text' => $datei ? text($datei) : '', 'format' => FORMAT_HTML, 'itemid' => $item];
                };
                $r = modul($course, 'workshop', [
                    'name' => $a['name'], 'intro' => $intro, 'introformat' => FORMAT_HTML, 'showdescription' => $zeige, 'visible' => $sichtbar,
                    'instructauthorseditor' => $editor($a['anleitung_autoren'] ?? '', $a['dateien_autoren'] ?? []),
                    'instructreviewerseditor' => $editor($a['anleitung_gutachter'] ?? '', $a['dateien_gutachter'] ?? []),
                    'conclusioneditor' => $editor($a['abschlusstext'] ?? '', []),
                    'grade' => $e['punkte_abgabe'] ?? 80, 'gradinggrade' => $e['punkte_beurteilung'] ?? 20,
                    'strategy' => 'accumulative', 'evaluation' => 'best', 'gradedecimals' => 0,
                    'submissiontypetext' => !empty($e['abgabe_text']) ? 1 : 0, 'submissiontypefile' => ($e['abgabe_datei'] ?? true) ? 1 : 0,
                    'nattachments' => $e['max_dateien'] ?? 1, 'submissionfiletypes' => implode(';', $e['erlaubte_dateitypen'] ?? []),
                    'maxbytes' => ($e['max_groesse_mb'] ?? 0) * 1024 * 1024, 'latesubmissions' => !empty($e['spaete_abgaben']) ? 1 : 0,
                    'useexamples' => 0, 'examplesmode' => 0, 'useselfassessment' => !empty($e['selbstbeurteilung']) ? 1 : 0, 'usepeerassessment' => 1,
                    'phaseswitchassessment' => 0, 'submissiongradepass' => 0, 'gradinggradepass' => 0,
                    'submissionstart' => 0, 'submissionend' => 0, 'assessmentstart' => 0, 'assessmentend' => 0,
                    'overallfeedbackmode' => 1, 'overallfeedbackfiles' => 0, 'overallfeedbackmaxbytes' => 0, 'overallfeedbackfiletypes' => '',
                ], $nr);
                $kriterien = $e['kriterien'] ?? [];
                if (!$kriterien) { fwrite(STDERR, "Workshop {$a['id']}: einstellungen.kriterien fehlt (mindestens ein Beurteilungskriterium)\n"); exit(1); }
                foreach (array_values($kriterien) as $k => $krit) {
                    $beschr = isset($krit['beschreibung_datei']) ? text($krit['beschreibung_datei']) : ($krit['beschreibung'] ?? '');
                    $DB->insert_record('workshopform_accumulative', (object) [
                        'workshopid' => $r->instance, 'sort' => $k + 1, 'description' => $beschr, 'descriptionformat' => FORMAT_HTML,
                        'grade' => $krit['punkte'] ?? 10, 'weight' => $krit['gewicht'] ?? 1]);
                }
                break;
            default:
                fwrite(STDERR, 'Unbekannte Art ' . $a['art'] . " bei {$a['id']} (erlaubt: label, page, url, file, assign, quiz, workshop)\n");
                exit(1);
        }
        $cm[$a['id']] = $r->coursemodule;
        if (!empty($a['einrueckung'])) { $DB->set_field('course_modules', 'indent', max(0, min(16, (int) $a['einrueckung'])), ['id' => $r->coursemodule]); }
        $instanz[$a['id']] = [$a['art'], $r->instance];
        echo sprintf("A%d %-7s cmid=%d  %s\n", $nr, $a['art'], $r->coursemodule, $a['name']);

        if ($a['art'] === 'quiz') {
            $quiz = $DB->get_record('quiz', ['id' => $r->instance], '*', MUST_EXIST);
            $quiz->cmid = $r->coursemodule;
            foreach ($fragen[$a['id']] as $qid) { quiz_add_quiz_question($qid, $quiz, 0); }
            quiz_repaginate_questions($quiz->id, 5);
            quiz_update_sumgrades($quiz);
            echo "   Fragen im Test: " . $DB->count_records('quiz_slots', ['quizid' => $quiz->id]) . ", Summe " . $DB->get_field('quiz', 'sumgrades', ['id' => $quiz->id]) . "\n";
        }
    }
}

// ---------- Link-Platzhalter {{LINK:id}} in Aufgabentexten und Seiten ----------
$ersetze = function ($roh) use ($cm, $alle, $CFG) {
    return preg_replace_callback('/\{\{LINK:([\w-]+)\}\}/', function ($m) use ($cm, $alle, $CFG) {
        if (!isset($cm[$m[1]])) { fwrite(STDERR, "Link-Ziel unbekannt: {$m[1]}\n"); exit(1); }
        $x = $alle[$m[1]];
        $modul = ['page' => 'page', 'assign' => 'assign', 'quiz' => 'quiz', 'file' => 'resource', 'url' => 'url', 'label' => 'label', 'workshop' => 'workshop'][$x['art']];
        return '<a href="' . $CFG->wwwroot . '/mod/' . $modul . '/view.php?id=' . $cm[$m[1]] . '">' . htmlspecialchars($x['name']) . '</a>';
    }, $roh);
};
foreach ($instanz as $id => [$art, $inst]) {
    if ($art === 'assign') { $feld = 'intro'; $tab = 'assign'; }
    elseif ($art === 'page') { $feld = 'content'; $tab = 'page'; }
    else { continue; }
    $alt = $DB->get_field($tab, $feld, ['id' => $inst]);
    if ($modus === 'abschnitt' && preg_match_all('/\{\{LINK:([\w-]+)\}\}/', $alt, $treffer)) {
        foreach ($treffer[1] as $ziel) {
            if (($wahl === 'alle' || $sektion[$id] === $wahl) && isset($sektion[$ziel]) && $sektion[$ziel] !== $sektion[$id]) { echo "WARNUNG: $id verlinkt $ziel in Abschnitt {$sektion[$ziel]}; der Link zeigt in der .mbz auf den Baukurs und wird nach dem Wiederherstellen ungültig\n"; }
        }
    }
    $neu = $ersetze($alt);
    if ($neu !== $alt) { $DB->set_field($tab, $feld, $neu, ['id' => $inst]); }
}
// ---------- Voraussetzungen (Zugriff erst nach Abschluss anderer Aktivitäten) ----------
foreach ($alle as $id => $a) {
    if (empty($a['voraussetzung'])) { continue; }
    $bed = []; $zeige = [];
    foreach ($a['voraussetzung'] as $vid) {
        if (!isset($cm[$vid])) { fwrite(STDERR, "Voraussetzung unbekannt: $vid (bei $id)\n"); exit(1); }
        if (($alle[$vid]['abschluss'] ?? 'keiner') === 'keiner') { fwrite(STDERR, "Voraussetzung $vid hat keinen Abschluss; bei $vid abschluss setzen\n"); exit(1); }
        if ($modus === 'abschnitt' && ($wahl === 'alle' || $sektion[$id] === $wahl) && $sektion[$vid] !== $sektion[$id]) { echo "WARNUNG: $id hat Voraussetzung $vid in Abschnitt {$sektion[$vid]}; in der Abschnitts-MBZ entfällt sie
"; }
        $bed[] = ['type' => 'completion', 'cm' => (int) $cm[$vid], 'e' => 1];
        $zeige[] = true;
    }
    $DB->set_field('course_modules', 'availability', json_encode(['op' => '&', 'c' => $bed, 'showc' => $zeige]), ['id' => $cm[$id]]);
}
rebuild_course_cache($course->id, true);

// ---------- Bewertungsschema (optional) ----------
if (!empty($plan['bewertung'])) {
    $b = $plan['bewertung'];
    $kurskat = grade_category::fetch_course_category($course->id);
    $kurskat->aggregation = GRADE_AGGREGATE_WEIGHTED_MEAN;
    $kurskat->aggregateonlygraded = 0;
    $kurskat->update();
    // Beim Wechsel von "Natürlich" auf gewichteten Mittelwert bleibt der alte Höchstwert stehen: auf 100 setzen
    $kursitem = $kurskat->get_grade_item();
    $kursitem->grademax = 100;
    $kursitem->grademin = 0;
    $kursitem->update();
    $gi = function ($id) use ($instanz, $course) {
        [$art, $inst] = $instanz[$id];
        $modul = ['assign' => 'assign', 'quiz' => 'quiz', 'page' => 'page', 'file' => 'resource', 'url' => 'url', 'workshop' => 'workshop'][$art];
        return grade_item::fetch(['courseid' => $course->id, 'itemtype' => 'mod', 'itemmodule' => $modul, 'iteminstance' => $inst, 'itemnumber' => 0]);
    };
    foreach ($b['kategorien'] ?? [] as $k) {
        $kat = new grade_category(['courseid' => $course->id, 'fullname' => $k['name']], false);
        $kat->apply_default_settings();
        $kat->apply_forced_settings();
        $kat->aggregation = GRADE_AGGREGATE_MEAN;
        $kat->aggregateonlygraded = 0;
        $kat->insert();
        $kat->set_parent($kurskat->id);
        foreach ($k['aktivitaeten'] as $id) { $g = $gi($id); if (!$g) { fwrite(STDERR, "Kein Bewertungselement für $id\n"); exit(1); } $g->set_parent($kat->id); }
        $katitem = $kat->get_grade_item();
        $katitem->aggregationcoef = $k['gewicht_prozent'];
        $katitem->update();
    }
    foreach ($b['gewichte'] ?? [] as $id => $w) {
        $g = $gi($id);
        if (!$g) { fwrite(STDERR, "Kein Bewertungselement für $id\n"); exit(1); }
        $g->aggregationcoef = $w;
        $g->update();
    }
    if (!empty($b['notenskala']['stufen'])) {
        $DB->delete_records('grade_letters', ['contextid' => $context->id]);
        foreach ($b['notenskala']['stufen'] as $st) {
            $DB->insert_record('grade_letters', (object) ['contextid' => $context->id, 'lowerboundary' => $st[0], 'letter' => $st[1]]);
        }
        $kursitem = $kurskat->get_grade_item();
        $kursitem->display = GRADE_DISPLAY_TYPE_PERCENTAGE_LETTER;
        $kursitem->decimals = 1;
        $kursitem->update();
    }
    grade_regrade_final_grades($course->id);
    echo "Bewertungsschema angelegt\n";
}

// ---------- Sicherung ----------
function sichern($typ, $id, $ziel, $mitbewertung) {
    global $USER;
    $bc = new backup_controller($typ, $id, backup::FORMAT_MOODLE, backup::INTERACTIVE_NO, backup::MODE_GENERAL, $USER->id);
    $p = $bc->get_plan();
    foreach (['users', 'anonymize', 'role_assignments', 'comments', 'badges', 'userscompletion', 'logs', 'grade_histories', 'groups', 'competencies', 'customfield', 'contentbankcontent', 'legacyfiles', 'calendarevents'] as $s) {
        if ($p->setting_exists($s)) { $p->get_setting($s)->set_value(false); }
    }
    foreach (['activities', 'blocks', 'filters', 'questionbank'] as $s) {
        if ($p->setting_exists($s)) { $p->get_setting($s)->set_value(true); }
    }
    $bc->set_status(backup::STATUS_AWAITING);
    $bc->execute_plan();
    $res = $bc->get_results();
    $res['backup_destination']->copy_content_to($ziel);
    $bc->destroy();
    echo "MBZ: $ziel (" . filesize($ziel) . " Bytes)\n";
}
$name = preg_replace('/[^A-Za-z0-9_-]+/', '_', $kurzname);
if ($modus === 'kurs') {
    sichern(backup::TYPE_1COURSE, $course->id, $ausgabe . $name . '_kurs.mbz', true);
} else {
    $ids = $wahl === 'alle' ? array_keys($abschnittid) : [$wahl];
    foreach ($ids as $aid) {
        if (!isset($abschnittid[$aid])) { fwrite(STDERR, "Abschnitt unbekannt: $aid (vorhanden: " . implode(', ', array_keys($abschnittid)) . ")\n"); exit(1); }
        sichern(backup::TYPE_1SECTION, $abschnittid[$aid], $ausgabe . $name . '_abschnitt_' . preg_replace('/[^A-Za-z0-9_-]+/', '_', $aid) . '.mbz', false);
    }
}
echo "KURSID={$course->id}\n";
