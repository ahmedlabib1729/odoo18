/** @odoo-module */

import { Component, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { stepUtils } from "@web_tour/tour_service/tour_utils";

import { embeddedViewPatchFunctions, endKnowledgeTour } from '../knowledge_tour_utils.js';
import { EmbeddedVideoComponent } from "@html_editor/others/embedded_components/core/video/video";

import { VideoSelector } from "@html_editor/main/media/media_dialog/video_selector";

//------------------------------------------------------------------------------
// UTILS
//------------------------------------------------------------------------------

const embeddedViewPatchUtil = embeddedViewPatchFunctions();

const embedViewSelector = (embedViewName) => {
    return `[data-embedded="view"]:has( .o_last_breadcrumb_item:contains("${embedViewName}"))`;
};

// This tour follows the 'knowledge_article_commands_tour'.
// As it contains a video, we re-use the Mock to avoid relying on actual YouTube content
let unpatchVideoEmbed;
let unpatchVideoSelector;

class MockedVideoIframe extends Component {
    static template = xml`
        <div class="o_video_iframe_src" t-out="props.src" />
    `;
    static props = ["src"];
}

const videoPatchSteps = [{ // patch the components
    trigger: "body",
    run: () => {
        unpatchVideoEmbed = patch(EmbeddedVideoComponent.components, {
            ...EmbeddedVideoComponent.components,
            VideoIframe: MockedVideoIframe
        });
        unpatchVideoSelector = patch(VideoSelector.components, {
            ...VideoSelector.components,
            VideoIframe: MockedVideoIframe
        });
    },
}];

const videoUnpatchSteps = [{ // unpatch the components
    trigger: "body",
    run: () => {
        unpatchVideoEmbed();
        unpatchVideoSelector();
    },
}];

//------------------------------------------------------------------------------
// TOUR STEPS - KNOWLEDGE COMMANDS
//------------------------------------------------------------------------------

/*
 * EMBED VIEW: /list
 * Checks that a user that has readonly access on an article cannot create items from the item list.
 * Note: this tour follows the 'knowledge_article_commands_tour', so we re-use the list name.
 */
const embedListName = "New Title";
const embedListSteps = [{ // scroll to the embedded view to load it
    trigger: embedViewSelector(embedListName),
    run: function () {
        this.anchor.scrollIntoView();
    },
}, { // wait for the list view to be mounted
    trigger: `${embedViewSelector(embedListName)} .o_list_renderer`,
}, { // check that the "new" button is not shown
    trigger: `${embedViewSelector(embedListName)} .o_control_panel_main:not(:has(.o_list_button_add))`,
}];

/*
 * EMBED VIEW: /kanban
 * Checks that a user that has readonly access on an article cannot create items from the item kanban.
 * Note: this tour follows the 'knowledge_article_commands_tour', so we re-use the kanban name.
 */
const embedKanbanName = "My Tasks Kanban";
const embedKanbanSteps = [{ // scroll to the embedded view to load it
    trigger: embedViewSelector(embedKanbanName),
    run: function () {
        this.anchor.scrollIntoView();
    },
}, { // wait for the kanban view to be mounted
    trigger: `${embedViewSelector(embedKanbanName)} .o_kanban_renderer`,
}, { // check that the "new" button and quick create buttons are not shown
    trigger: `${embedViewSelector(embedKanbanName)}:not(:has(.o-kanban-button-new)):not(:has(.o_kanban_quick_add))`,
}];

registry.category("web_tour.tours").add('knowledge_article_commands_readonly_tour', {
    url: '/odoo',
    test: true,
    steps: () => [stepUtils.showAppsMenuItem(), {
    // open the Knowledge App
    trigger: '.o_app[data-menu-xmlid="knowledge.knowledge_menu_root"]',
    run: "click",
},
    ...videoPatchSteps,
{
    trigger: "body",
    run: () => {
        embeddedViewPatchUtil.before();
    },
},
    ...embedListSteps,
    ...embedKanbanSteps,
    ...videoUnpatchSteps,
{
    trigger: "body",
    run: () => {
        embeddedViewPatchUtil.after();
    },
},
    ...endKnowledgeTour()
]});
