import { Plugin } from "@html_editor/plugin";
import { paragraphRelatedElements } from "@html_editor/utils/dom_info";

export class AutofocusPlugin extends Plugin {
    static name = "autofocus";
    static dependencies = ["selection"];

    handleCommand(command, payload) {
        switch (command) {
            case "START_EDITION": {
                this.focusFirstElement();
                break;
            }
        }
    }

    focusFirstElement() {
        for (const paragraph of this.editable.querySelectorAll(
            paragraphRelatedElements.join(", ")
        )) {
            if (paragraph.isContentEditable) {
                const { anchorNode, anchorOffset, focusNode, focusOffset } =
                    this.shared.setSelection({
                        anchorNode: paragraph,
                        anchorOffset: 0,
                    });
                const selectionData = this.shared.getSelectionData();
                if (!selectionData.documentSelectionIsInEditable) {
                    const selection = this.document.getSelection();
                    selection.setBaseAndExtent(anchorNode, anchorOffset, focusNode, focusOffset);
                }
                break;
            }
        }
    }
}
