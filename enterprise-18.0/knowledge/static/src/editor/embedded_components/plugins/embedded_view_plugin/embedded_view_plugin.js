import { Plugin } from "@html_editor/plugin";
import { closestElement } from "@html_editor/utils/dom_traversal";
import { ItemCalendarPropsDialog } from "@knowledge/components/item_calendar_props_dialog/item_calendar_props_dialog";
import { PromptEmbeddedViewNameDialog } from "@knowledge/components/prompt_embedded_view_name_dialog/prompt_embedded_view_name_dialog";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";

function isAvailable(node) {
    return (
        !!closestElement(node, ".o_editor_banner") ||
        !!closestElement(node, "table") ||
        !!closestElement(node, "[data-embedded]")
    );
}

export class EmbeddedViewPlugin extends Plugin {
    static name = "embeddedView";
    static dependencies = ["dom", "selection", "embedded_components"];
    resources = {
        powerboxItems: [
            {
                category: "knowledge",
                name: _t("Item Kanban"),
                description: _t("Insert a Kanban view of article items"),
                fontawesome: "fa-th-large",
                isAvailable,
                action: () => {
                    this.promptInsertEmbeddedView("kanban", true);
                },
            },
            {
                category: "knowledge",
                name: _t("Item Cards"),
                description: _t("Insert a Card view of article items"),
                fontawesome: "fa-address-card",
                isAvailable,
                action: () => {
                    this.promptInsertEmbeddedView("kanban");
                },
            },
            {
                category: "knowledge",
                name: _t("Item List"),
                description: _t("Insert a List view of article items"),
                fontawesome: "fa-th-list",
                isAvailable,
                action: () => {
                    this.promptInsertEmbeddedView("list");
                },
            },
            {
                category: "knowledge",
                name: _t("Item Calendar"),
                description: _t("Insert a Calendar view of article items"),
                fontawesome: "fa-calendar-plus-o",
                isAvailable,
                action: () => {
                    this.promptInsertEmbeddedCalendarView();
                },
            },
        ],
    };

    insertEmbeddedView(actionXmlId, name, viewType, additionalViewProps = {}) {
        const resId = this.config.getRecordInfo().resId;
        const embeddedViewBlueprint = renderToElement("knowledge.EmbeddedViewBlueprint", {
            embeddedProps: JSON.stringify({
                viewProps: {
                    actionXmlId,
                    additionalViewProps,
                    context: {
                        active_id: resId,
                        default_parent_id: resId,
                        default_is_article_item: true,
                    },
                    displayName: name,
                    viewType,
                },
            }),
        });
        this.shared.domInsert(embeddedViewBlueprint);
        this.dispatch("ADD_STEP");
    }

    promptInsertEmbeddedCalendarView() {
        let cursor = this.shared.preserveSelection();
        const resId = this.config.getRecordInfo().resId;
        this.services.dialog.add(
            ItemCalendarPropsDialog,
            {
                isNew: true,
                knowledgeArticleId: resId,
                saveItemCalendarProps: (name, itemCalendarProps) => {
                    cursor = null;
                    this.insertEmbeddedView(
                        "knowledge.knowledge_article_action_item_calendar",
                        name,
                        "calendar",
                        { itemCalendarProps }
                    );
                },
            },
            {
                onClose: () => {
                    cursor?.restore();
                },
            }
        );
    }

    promptInsertEmbeddedView(viewType, withStages) {
        let cursor = this.shared.preserveSelection();
        const resId = this.config.getRecordInfo().resId;
        this.services.dialog.add(
            PromptEmbeddedViewNameDialog,
            {
                isNew: true,
                save: async (name) => {
                    cursor = null;
                    if (withStages) {
                        await this.services.orm.call(
                            "knowledge.article",
                            "create_default_item_stages",
                            [resId]
                        );
                    }
                    this.insertEmbeddedView(
                        `knowledge.knowledge_article_item_action${withStages ? "_stages" : ""}`,
                        name,
                        viewType
                    );
                },
                viewType,
            },
            {
                onClose: () => {
                    cursor?.restore();
                },
            }
        );
    }
}
