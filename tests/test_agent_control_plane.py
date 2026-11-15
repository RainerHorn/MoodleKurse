from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOTS = (
    "didaktik",
    "fiae",
    "fidp",
    "fisi",
    "moodle-mbz",
    "moodle-mcp",
    "orchestrator",
    "quiz",
    "reviewer",
    "visual-designer",
    "vt",
)
SPECIALISTS = tuple(bot for bot in BOTS if bot != "orchestrator")


class AgentControlPlaneTests(unittest.TestCase):
    def test_agents_md_defines_single_control_path(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
        required = (
            "`hermes` uebergibt den konsolidierten Auftrag ausschliesslich an `orchestrator`",
            "Nur `orchestrator` beauftragt Fach-, Didaktik-, Quiz-, Design-, Review- und Moodle-Rollen",
            "Spezialisten beauftragen keine anderen Rollen",
            "`[SILENT]`",
            "Hop-Limits werden nicht erhoeht",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_every_profile_has_control_plane_skill(self) -> None:
        # One source under agents/_shared; profile_sync distributes it to every role.
        relative = "skills/moodle-agent-control-plane/SKILL.md"
        source = "agents/_shared/" + relative
        text = (ROOT / source).read_text(encoding="utf-8-sig")
        self.assertIn("Nur der Orchestrator beauftragt", text)
        self.assertIn("Spezialisten beauftragen keine anderen Rollen", text)
        self.assertIn("nicht mit `[SILENT]` enden", text)
        self.assertIn("Hop-Limits werden nicht erhöht", text)
        self.assertIn("message_agent(expects_reply=false)", text)
        self.assertIn("Nur die finale Antwort im noch laufenden ursprünglichen Hermes-Auftrag", text)
        spec = importlib.util.spec_from_file_location("profile_sync", ROOT / "scripts" / "profile_sync.py")
        sync = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sync)
        mapping = sync.sources(ROOT)
        for bot in BOTS:
            with self.subTest(bot=bot):
                self.assertEqual(source, mapping.get(bot + "/" + relative))
                self.assertFalse((ROOT / "agents" / bot / relative).exists(), "Role copy would drift")

    def test_specialist_souls_enforce_return_to_orchestrator(self) -> None:
        for bot in SPECIALISTS:
            text = (ROOT / "agents" / bot / "SOUL.md").read_text(encoding="utf-8-sig")
            with self.subTest(bot=bot):
                self.assertIn("moodle-agent-control-plane", text)
                self.assertIn("Orchestrator", text)
                self.assertIn("[SILENT]", text)
                self.assertIn("Hop-Limits", text)
                if bot == "reviewer":
                    self.assertIn("beauftragst weder Korrekturrollen noch andere Spezialisten", text)
                else:
                    self.assertIn("beauftragst keine anderen Rollen", text)

    def test_orchestrator_soul_enforces_entry_and_return_path(self) -> None:
        text = (ROOT / "agents" / "orchestrator" / "SOUL.md").read_text(encoding="utf-8-sig")
        required = (
            "entweder der Benutzer direkt in deinem Chat oder",
            "Nur du beauftragst die Spezialisten",
            "meldest du aktiv an den Auftraggeber zurueck",
            "Rueckfragen an den Benutzer stellst nur du",
            "hoechstens zwei Wellen",
            "startest du keine weitere Korrekturwelle",
            "moodle-agent-control-plane",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        self.assertNotIn("einzige Schnittstelle zum Benutzer", text)

    def test_two_entry_points_chains_and_second_rejection_gate(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
        workflow = (ROOT / "docs" / "mbz-workflow.md").read_text(encoding="utf-8-sig")
        skill = (ROOT / "agents/_shared/skills/moodle-agent-control-plane/SKILL.md").read_text(encoding="utf-8-sig")
        hermes = (ROOT / "agents/_shared/hermes/SOUL.md").read_text(encoding="utf-8-sig")
        for text in (agents, skill):
            self.assertIn("direkt", text)
            self.assertIn("drei", text)
            self.assertIn("`REJECTED`", text)
            self.assertIn("Benutzergate", text)
        self.assertIn("agents/_shared/hermes/SOUL.md", agents)
        self.assertIn("## Ketten", workflow)
        for chain in ("| 1 Materialien |", "| 2 Review |", "| 3 Delta-Review |"):
            self.assertIn(chain, workflow)
        self.assertNotIn("| 4 Bau |", workflow)
        self.assertIn("genau einen konsolidierten Auftrag", hermes)
        self.assertIn("beauftragst nie eine andere", hermes)
        self.assertIn("Hop-Limits werden nicht erhoeht", hermes)
        # The entry file must not be mistaken for a role by the profile sync.
        self.assertFalse((ROOT / "agents" / "hermes" / "SOUL.md").exists())

    def test_gate_differs_by_variant_and_mcp_lives_in_appendix(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
        appendix = (ROOT / "docs" / "mcp-anhang.md").read_text(encoding="utf-8-sig")
        check = (ROOT / "_vorgaben/qualitaetsstandards/pruefstrategie.md").read_text(encoding="utf-8-sig")
        self.assertIn("finale `.mbz` ohne weitere Benutzerfreigabe", agents)
        self.assertIn("ausdrueckliche Benutzerfreigabe fuer den konkreten", agents)
        self.assertIn("`moodle_delete_module` soll nicht freigegeben werden", agents)
        self.assertIn("Benutzerfreigabe für genau diesen Plan", appendix)
        self.assertIn("`verified=1`", appendix)
        self.assertNotIn("`verified=1`", check)
        for bot in SPECIALISTS:
            if bot == "moodle-mcp":
                continue
            text = (ROOT / "agents" / bot / "SOUL.md").read_text(encoding="utf-8-sig")
            with self.subTest(bot=bot):
                self.assertNotIn("(MCP oder MBZ)", text)
                self.assertNotIn("__MOODLE_URL", text)
                self.assertNotIn("xml_transport", text)

    def test_specialists_do_not_ask_the_user_directly(self) -> None:
        text = (ROOT / "agents" / "moodle-mbz" / "SOUL.md").read_text(encoding="utf-8-sig")
        self.assertIn("Du fragst den\nBenutzer in einer Kursproduktion nicht selbst", text)

    def test_didaktik_does_not_contact_specialists_directly(self) -> None:
        text = (ROOT / "agents" / "didaktik" / "SOUL.md").read_text(encoding="utf-8-sig")
        self.assertNotIn("fragst du den Fachagenten", text)
        self.assertIn("meldest du den Klaerungsbedarf an den Orchestrator", text)


if __name__ == "__main__":
    unittest.main()
