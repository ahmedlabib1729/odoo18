import { defineDocumentSpreadsheetModels } from "@documents_spreadsheet/../tests/helpers/data";
import {
    createSpreadsheet,
    displayedConnectedUsers,
    getConnectedUsersElImage,
    getSynchedStatus,
} from "@documents_spreadsheet/../tests/helpers/spreadsheet_test_utils";
import { beforeEach, expect, getFixture, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";
import { setCellContent } from "@spreadsheet/../tests/helpers/commands";
import {
    joinSession,
    leaveSession,
} from "@spreadsheet_edition/../tests/helpers/collaborative_helpers";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";

defineDocumentSpreadsheetModels();

/** @type {HTMLElement} */
let target;

beforeEach(() => {
    target = getFixture();
});

test("Number of connected users is correctly rendered", async function () {
    const { transportService } = await createSpreadsheet();
    expect(displayedConnectedUsers(target)).toBe(1, {
        message: "It should display one connected user",
    });
    expect(getConnectedUsersElImage(target)).toHaveClass("fa-user", {
        message: "It should display the fa-user icon",
    });
    joinSession(transportService, { id: 1234, userId: 9999 });
    await animationFrame();
    expect(displayedConnectedUsers(target)).toBe(2, {
        message: "It should display two connected users",
    });
    expect(getConnectedUsersElImage(target)).toHaveClass("fa-users", {
        message: "It should display the fa-users icon",
    });

    // The same user is connected with two different tabs.
    joinSession(transportService, { id: 4321, userId: 9999 });
    await animationFrame();
    expect(displayedConnectedUsers(target)).toBe(2, {
        message: "It should display two connected users",
    });

    leaveSession(transportService, 4321);
    await animationFrame();
    expect(displayedConnectedUsers(target)).toBe(2, {
        message: "It should display two connected users",
    });

    leaveSession(transportService, 1234);
    await animationFrame();
    expect(displayedConnectedUsers(target)).toBe(1, {
        message: "It should display one connected user",
    });
});

test("collaborative session client has the user id", async function () {
    const uid = user.userId;
    const { model } = await createSpreadsheet();
    const clients = [...model.getters.getConnectedClients()];
    expect(clients.length).toBe(1);
    const localClient = clients[0];
    expect(localClient.name).toBe(user.name);
    expect(localClient.userId).toBe(uid);
});

test("Sync status is correctly rendered", async function () {
    const { model, transportService } = await createSpreadsheet();
    await animationFrame();
    expect(getSynchedStatus(target)).toBe(" Saved");
    await transportService.concurrent(async () => {
        setCellContent(model, "A1", "hello");
        await animationFrame();
        expect(getSynchedStatus(target)).toBe(" Saving");
    });
    await animationFrame();
    expect(getSynchedStatus(target)).toBe(" Saved");
});

test("receiving bad revision reload", async function () {
    const serviceRegistry = registry.category("services");
    serviceRegistry.add("actionMain", serviceRegistry.get("action"));
    const fakeActionService = {
        dependencies: ["actionMain"],
        start(env, { actionMain }) {
            return Object.assign({}, actionMain, {
                doAction: (actionRequest, options = {}) => {
                    if (actionRequest === "reload_context") {
                        expect.step("reload");
                        return Promise.resolve();
                    }
                    return actionMain.doAction(actionRequest, options);
                },
            });
        },
    };
    serviceRegistry.add("action", fakeActionService, { force: true });
    const { transportService } = await createSpreadsheet();
    transportService.broadcast({
        type: "REMOTE_REVISION",
        serverRevisionId: "an invalid revision id",
        nextRevisionId: "the next revision id",
        revision: {},
    });
    expect.verifySteps(["reload"]);
});
