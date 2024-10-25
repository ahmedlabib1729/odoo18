import { Plugin } from "@html_editor/plugin";
import { isPhrasingContent } from "@html_editor/utils/dom_info";

export class InsertPendingElementPlugin extends Plugin {
    static name = "insertPendingElement";
    static dependencies = ["dom", "selection", "embedded_components"];

    handleCommand(command, payload) {
        switch (command) {
            case "START_EDITION":
                this.insertEmbeddedBluePrint();
                break;
        }
    }

    insertEmbeddedBluePrint() {
        const { resModel, resId } = this.config.getRecordInfo();
        const embeddedBlueprint =
            this.services.knowledgeCommandsService.popPendingEmbeddedBlueprint({
                field: "body",
                resId,
                model: resModel,
            });
        if (embeddedBlueprint) {
            let insert;
            if (isPhrasingContent(embeddedBlueprint)) {
                insert = () => {
                    // insert phrasing content
                    const paragraph = document.createElement("p");
                    paragraph.appendChild(embeddedBlueprint);
                    this.shared.setCursorEnd(this.editable);
                    this.shared.domInsert(paragraph);
                    this.dispatch("ADD_STEP");
                };
            } else {
                insert = () => {
                    // insert block content
                    this.shared.setCursorEnd(this.editable);
                    this.shared.domInsert(embeddedBlueprint);
                    const paragraph = document.createElement("p");
                    paragraph.appendChild(document.createElement("br"));
                    this.shared.setCursorEnd(this.editable);
                    this.shared.domInsert(paragraph);
                    this.dispatch("ADD_STEP");
                };
            }
            insert();
            this.editable.addEventListener("onHistoryResetFromPeer", insert, { once: true });
        }
    }
}
