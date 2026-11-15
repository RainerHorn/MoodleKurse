<?php
// Stellt eine .mbz im lokalen Moodle wieder her (Probe).
// Aufruf: php restore.php <datei.mbz> neu|bestehend [zielkursid]
//   neu        Wiederherstellen als neuer Kurs (Kategorie 1)
//   bestehend  Zusammenführen in einen bestehenden Kurs (wie "In bestehenden Kurs einfügen", ohne Löschen);
//              ohne zielkursid wird ein leerer Testkurs "MBZ-ZIEL" angelegt (Umgebungsvariable MBZ_ZIEL_OHNE_NAMEN=1: Abschnitte ohne Namen,
//              wie ein frischer Moodle-Abschnitt; MBZ_ZIELNUMMER = Anzahl der Abschnitte)
// Gibt "RESTORED=<kursid>" aus.
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->dirroot . '/backup/util/includes/restore_includes.php');
\core\session\manager::set_user(get_admin());
global $DB, $USER;

$datei = $argv[1] ?? '';
$ziel = $argv[2] ?? 'neu';
if (!is_file($datei)) { fwrite(STDERR, "MBZ fehlt: $datei\n"); exit(1); }

$tmp = 'mbzprobe_' . uniqid();
$pfad = $CFG->tempdir . '/backup/' . $tmp;
check_dir_exists($pfad, true, true);
$packer = get_file_packer('application/vnd.moodle.backup');
if (!$packer->extract_to_pathname($datei, $pfad)) { fwrite(STDERR, "Entpacken fehlgeschlagen\n"); exit(1); }

if ($ziel === 'neu') {
    $info = backup_general_helper::get_backup_information($tmp);
    $kursid = restore_dbops::create_new_course($info->original_course_fullname . ' (Probe ' . date('His') . ')', 'PROBE' . date('His') . rand(10, 99), 1);
    $target = backup::TARGET_NEW_COURSE;
} else {
    $kursid = (int) ($argv[3] ?? 0);
    if (!$kursid) {
        if ($alt = $DB->get_record('course', ['shortname' => 'MBZ-ZIEL'])) { delete_course($alt, false); }
        $d = (object) ['fullname' => 'MBZ-Ziel (Testkurs)', 'shortname' => 'MBZ-ZIEL', 'category' => 1, 'format' => 'topics', 'summary' => '', 'summaryformat' => FORMAT_HTML, 'visible' => 1, 'enablecompletion' => 0];
        $z = create_course($d);
        $n = max(1, (int) getenv('MBZ_ZIELNUMMER'));
        course_create_sections_if_missing($z, range(1, $n));
        for ($k = 1; $k <= $n && !getenv('MBZ_ZIEL_OHNE_NAMEN'); $k++) { course_update_section($z, $DB->get_record('course_sections', ['course' => $z->id, 'section' => $k], '*', MUST_EXIST), ['name' => 'Vorhandener Abschnitt ' . $k]); }
        $kursid = $z->id;
    }
    $target = backup::TARGET_EXISTING_ADDING;
}
$rc = new restore_controller($tmp, $kursid, backup::INTERACTIVE_NO, backup::MODE_GENERAL, $USER->id, $target);
if ($target == backup::TARGET_EXISTING_ADDING && $rc->get_plan()->setting_exists('overwrite_conf')) { $rc->get_plan()->get_setting('overwrite_conf')->set_value(false); }
if (!$rc->execute_precheck()) {
    $r = $rc->get_precheck_results();
    fwrite(STDERR, 'Vorprüfung: ' . json_encode($r, JSON_UNESCAPED_UNICODE) . "\n");
    if (!empty($r['errors'])) { exit(1); }
}
$rc->execute_plan();
$rc->destroy();
fulldelete($pfad);
rebuild_course_cache($kursid, true);
echo "RESTORED=$kursid\n";

