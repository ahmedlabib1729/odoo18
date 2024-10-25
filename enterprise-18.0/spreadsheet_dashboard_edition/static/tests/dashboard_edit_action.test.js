import { Deferred } from "@web/core/utils/concurrency";
import { patchWithCleanup, MockServer, contains } from "@web/../tests/web_test_helpers";
import { animationFrame } from "@odoo/hoot-mock";
import { expect, test, getFixture } from "@odoo/hoot";
import { registry } from "@web/core/registry";
import { actionService } from "@web/webclient/actions/action_service";
import { browser } from "@web/core/browser/browser";
import {
    defineSpreadsheetDashboardEditionModels,
    getDashboardBasicServerData,
} from "./helpers/test_data";
import { createDashboardEditAction, createNewDashboard } from "./helpers/test_helpers";
import { getCellContent } from "@spreadsheet/../tests/helpers/getters";
import { doMenuAction } from "@spreadsheet/../tests/helpers/ui";
import { registries } from "@odoo/o-spreadsheet";

defineSpreadsheetDashboardEditionModels();

const { topbarMenuRegistry } = registries;

test("open dashboard with existing data", async function () {
    const serverData = getDashboardBasicServerData();
    const spreadsheetId = createNewDashboard(serverData, {
        sheets: [
            {
                cells: {
                    A1: { content: "Hello" },
                },
            },
        ],
    });
    const { model } = await createDashboardEditAction({ serverData, spreadsheetId });
    expect(getCellContent(model, "A1")).toBe("Hello");
});

test("copy dashboard from topbar menu", async function () {
    const serviceRegistry = registry.category("services");
    serviceRegistry.add("actionMain", actionService);
    const fakeActionService = {
        dependencies: ["actionMain"],
        start(env, { actionMain }) {
            return {
                ...actionMain,
                doAction: (actionRequest, options = {}) => {
                    if (
                        actionRequest.tag === "action_edit_dashboard" &&
                        actionRequest.params.spreadsheet_id === 111
                    ) {
                        expect.step("redirect");
                    } else {
                        return actionMain.doAction(actionRequest, options);
                    }
                },
            };
        },
    };
    serviceRegistry.add("action", fakeActionService, { force: true });
    const { env } = await createDashboardEditAction({
        mockRPC: function (route, args) {
            if (args.model == "spreadsheet.dashboard" && args.method === "copy") {
                expect.step("dashboard_copied");
                const { spreadsheet_data, thumbnail } = args.kwargs.default;
                expect(spreadsheet_data).not.toBe(undefined);
                expect(thumbnail).not.toBe(undefined);
                return [111];
            }
        },
    });
    await doMenuAction(topbarMenuRegistry, ["file", "make_copy"], env);
    expect.verifySteps(["dashboard_copied", "redirect"]);
});

test("share dashboard from control panel", async function () {
    const target = getFixture();
    const serverData = getDashboardBasicServerData();
    const spreadsheetId = createNewDashboard(serverData, {
        sheets: [
            {
                cells: {
                    A1: { content: "Hello" },
                },
            },
        ],
    });
    patchWithCleanup(browser.navigator.clipboard, {
        writeText: async (url) => {
            expect.step("share url copied");
            expect(url).toBe("localhost:8069/share/url/132465");
        },
    });
    const def = new Deferred();
    const { model } = await createDashboardEditAction({
        serverData,
        spreadsheetId,
        mockRPC: async function (route, args) {
            if (args.method === "action_get_share_url") {
                await def;
                expect.step("dashboard_shared");
                const [shareVals] = args.args;
                expect(args.model).toBe("spreadsheet.dashboard.share");
                const excel = JSON.parse(JSON.stringify(model.exportXLSX().files));
                expect(shareVals).toEqual({
                    spreadsheet_data: JSON.stringify(model.exportData()),
                    dashboard_id: spreadsheetId,
                    excel_files: excel,
                });
                return "localhost:8069/share/url/132465";
            }
        },
    });
    expect(target.querySelector(".spreadsheet_share_dropdown")).toBe(null);
    await contains("i.fa-share-alt").click();
    expect(".spreadsheet_share_dropdown").toHaveText("Generating sharing link");
    def.resolve();
    await animationFrame();
    expect.verifySteps(["dashboard_shared", "share url copied"]);
    expect(".o_field_CopyClipboardChar").toHaveText("localhost:8069/share/url/132465");
    await contains(".fa-clone").click();
    expect.verifySteps(["share url copied"]);
});

test("publish dashboard from control panel", async function () {
    const fixture = getFixture();
    await createDashboardEditAction({
        mockRPC: async function (route, args) {
            if (args.model === "spreadsheet.dashboard" && args.method === "write") {
                expect.step("dashboard_published");
                expect(args.args[1]).toEqual({ is_published: true });
            }
        },
    });
    const checkbox = fixture.querySelector(".o_sp_publish_dashboard .o-checkbox input");
    expect(fixture.querySelector(".o_sp_publish_dashboard").textContent).toInclude("Unpublished");
    expect(checkbox).not.toBeChecked();
    await contains(".o_sp_publish_dashboard").click();
    expect(checkbox).toBeChecked();
    expect(fixture.querySelector(".o_sp_publish_dashboard").textContent).toInclude("Published");
    expect.verifySteps(["dashboard_published"]);
});

test("unpublish dashboard from control panel", async function () {
    const fixture = getFixture();
    await createDashboardEditAction({
        mockRPC: async function (route, args, performRPC) {
            if (args.model === "spreadsheet.dashboard" && args.method === "write") {
                expect.step("dashboard_unpublished");
                expect(args.args[1]).toEqual({ is_published: false });
            }
            if (
                args.model === "spreadsheet.dashboard" &&
                args.method === "join_spreadsheet_session"
            ) {
                return {
                    ...(await MockServer.current.callOrm({ route, ...args })),
                    is_published: true,
                };
            }
        },
    });
    const checkbox = fixture.querySelector(".o_sp_publish_dashboard .o-checkbox input");
    expect(fixture.querySelector(".o_sp_publish_dashboard").textContent).toInclude("Published");
    expect(checkbox).toBeChecked();
    await contains(".o_sp_publish_dashboard").click();
    expect(checkbox).not.toBeChecked();
    expect(fixture.querySelector(".o_sp_publish_dashboard").textContent).toInclude("Unpublished");
    expect.verifySteps(["dashboard_unpublished"]);
});
