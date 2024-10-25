import {
    htmlEditorVersions,
    stripVersion,
    VERSION_SELECTOR,
} from "@knowledge/editor/html_migrations/manifest";
import { Plugin } from "@html_editor/plugin";

export class VersionPlugin extends Plugin {
    static name = "version";

    handleCommand(command, payload) {
        switch (command) {
            case "CLEAN_FOR_SAVE":
                this.cleanForSave(payload.root);
                break;
            case "NORMALIZE":
                this.normalize(payload.node);
                break;
        }
    }

    normalize(parent) {
        if (parent.matches(VERSION_SELECTOR) && parent !== this.editable) {
            delete parent.dataset.oeVersion;
        }
        stripVersion(parent);
    }

    cleanForSave(root) {
        const VERSIONS = htmlEditorVersions();
        const firstChild = root.firstElementChild;
        const version = VERSIONS.at(-1);
        if (firstChild && version) {
            firstChild.dataset.oeVersion = version;
        }
    }
}
