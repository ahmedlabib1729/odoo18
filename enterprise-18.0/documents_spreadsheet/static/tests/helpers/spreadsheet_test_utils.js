import { SpreadsheetAction } from "@documents_spreadsheet/bundle/actions/spreadsheet_action";
import { SpreadsheetTemplateAction } from "@documents_spreadsheet/bundle/actions/spreadsheet_template/spreadsheet_template_action";
import { animationFrame } from "@odoo/hoot-mock";
import { getBasicServerData } from "@spreadsheet/../tests/helpers/data";
import { makeDocumentsSpreadsheetMockEnv } from "@documents_spreadsheet/../tests/helpers/model";
import { UNTITLED_SPREADSHEET_NAME } from "@spreadsheet/helpers/constants";
import {
    getSpreadsheetActionEnv,
    getSpreadsheetActionModel,
    prepareWebClientForSpreadsheet,
} from "@spreadsheet_edition/../tests/helpers/webclient_helpers";
import {
    getService,
    mockService,
    mountWithCleanup,
    patchTranslations,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import { WebClient } from "@web/webclient/webclient";
import { DocumentsDocument, SpreadsheetTemplate } from "./data";
import { getMockEnv } from "@web/../tests/_framework/env_test_helpers";

/**
 * @typedef {import("@spreadsheet/../tests/helpers/data").ServerData} ServerData
 */

/**
 * @typedef {object} SpreadsheetTestParams
 * @property {object} [webClient] Webclient already configured
 * @property {number} [spreadsheetId] Id of the spreadsheet
 * @property {ServerData} [serverData] Data to be injected in the mock server
 * @property {Function} [mockRPC] Mock rpc function
 */

/**
 * Open a spreadsheet action
 *
 * @param {string} actionTag Action tag ("action_open_spreadsheet" or "action_open_template")
 * @param {SpreadsheetTestParams} params
 */
async function createSpreadsheetAction(actionTag, params) {
    const SpreadsheetActionComponent =
        actionTag === "action_open_spreadsheet" ? SpreadsheetAction : SpreadsheetTemplateAction;
    const { webClient } = params;
    /** @type {any} */
    let spreadsheetAction;
    patchWithCleanup(SpreadsheetActionComponent.prototype, {
        setup() {
            super.setup();
            spreadsheetAction = this;
        },
    });
    if (!webClient) {
        await prepareWebClientForSpreadsheet();
        await makeDocumentsSpreadsheetMockEnv(params);
        await mountWithCleanup(WebClient);
    }
    await getService("action").doAction(
        {
            type: "ir.actions.client",
            tag: actionTag,
            params: {
                spreadsheet_id: params.spreadsheetId,
            },
        },
        { clearBreadcrumbs: true } // Sometimes in test defining custom action, Odoo opens on the action instead of opening on root
    );
    await animationFrame();
    const model = getSpreadsheetActionModel(spreadsheetAction);
    return {
        webClient,
        model,
        env: getSpreadsheetActionEnv(spreadsheetAction),
        transportService: model.config.transportService,
    };
}

/**
 * Create an empty spreadsheet
 *
 * @param {SpreadsheetTestParams} params
 */
export async function createSpreadsheet(params = {}) {
    patchTranslations();
    if (!params.serverData) {
        params.serverData = getBasicServerData();
    }
    if (!params.spreadsheetId) {
        const documents = DocumentsDocument._records;
        const spreadsheetId = Math.max(...documents.map((d) => d.id)) + 1;
        documents.push({
            id: spreadsheetId,
            name: UNTITLED_SPREADSHEET_NAME.toString(), // toString() to force translation
            spreadsheet_data: "{}",
            active: true,
        });
        params = { ...params, spreadsheetId };
    }
    return createSpreadsheetAction("action_open_spreadsheet", params);
}

/**
 * Create a spreadsheet template
 *
 * @param {SpreadsheetTestParams} params
 */
export async function createSpreadsheetTemplate(params = {}) {
    if (!params.serverData) {
        params.serverData = getBasicServerData();
    }
    if (!params.spreadsheetId) {
        const templates = SpreadsheetTemplate._records;
        const spreadsheetId = Math.max(...templates.map((d) => d.id)) + 1;
        templates.push({
            id: spreadsheetId,
            name: "test template",
            spreadsheet_data: "{}",
        });
        params = { ...params, spreadsheetId };
    }
    return createSpreadsheetAction("action_open_template", params);
}

/**
 * Mock the action service of the env, and add the mockDoAction function to it.
 */
export function mockActionService(mockDoAction) {
    const env = getMockEnv();
    if (!env) {
        mockService("action", { doAction: mockDoAction });
    } else {
        patchWithCleanup(env.services.action, {
            doAction(action, options) {
                mockDoAction(action, options);
            },
        });
    }
}

/**
 * @param {HTMLElement} target
 * @returns {HTMLElement}
 */
export function getConnectedUsersEl(target) {
    return target.querySelector(".o_spreadsheet_number_users");
}

/**
 * @param {HTMLElement} target
 * @returns {HTMLElement}
 */
export function getConnectedUsersElImage(target) {
    return target.querySelector(".o_spreadsheet_number_users i");
}

/**
 *
 * @param {HTMLElement} target
 * @returns {string}
 */
export function getSynchedStatus(target) {
    /** @type {HTMLElement} */
    const content = target.querySelector(".o_spreadsheet_sync_status");
    return content.innerText;
}

/**
 * @param {HTMLElement} target
 * @returns {number}
 */
export function displayedConnectedUsers(target) {
    return parseInt(getConnectedUsersEl(target).innerText);
}
