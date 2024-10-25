import { Plugin } from "@html_editor/plugin";
import { closestElement } from "@html_editor/utils/dom_traversal";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";

export class EmbeddedClipboardPlugin extends Plugin {
    static name = "embeddedClipboard";
    static dependencies = ["embedded_components", "dom", "selection"];
     resources = {
        powerboxItems: [
            {
                category: "media",
                name: _t("Clipboard"),
                description: _t("Add a clipboard section"),
                fontawesome: "fa-pencil-square",
                isAvailable: (node) => !!closestElement(node, "[data-embedded='clipboard']"),
                action: () => {
                    this.insertClipboard();
                },
            },
        ],
    };

    handleCommand(command, payload) {
        switch (command) {
            case "SETUP_NEW_COMPONENT":
                this.setupNewClipboard(payload);
                break;
        }
    }

    insertClipboard() {
        const clipboardBlock = renderToElement("knowledge.EmbeddedClipboardBlueprint");
        this.shared.domInsert(clipboardBlock);
        this.shared.setCursorStart(clipboardBlock.querySelector("p"));
        this.dispatch("ADD_STEP");
    }

    setupNewClipboard({ name, env }) {
        if (name === "clipboard") {
            Object.assign(env, {
                editorShared: {
                    preserveSelection: this.shared.preserveSelection,
                },
            });
        }
    }
}
