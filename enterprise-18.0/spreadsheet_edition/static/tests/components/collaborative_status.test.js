import { makeMockEnv } from "@web/../tests/web_test_helpers";
import { defineSpreadsheetModels } from "@spreadsheet/../tests/helpers/data";
import { describe, expect, test, getFixture, mountOnFixture } from "@odoo/hoot";
import { getTemplate } from "@web/core/templates";

import { CollaborativeStatus } from "@spreadsheet_edition/bundle/components/collaborative_status/collaborative_status";

describe.current.tags("headless");
defineSpreadsheetModels();

async function mountCollaborativeStatusComponent(env) {
    await mountOnFixture(CollaborativeStatus, { props: {}, env, getTemplate });
}

test("not synchronized", async function () {
    const env = await makeMockEnv({
        model: {
            getters: {
                isFullySynchronized: () => false,
                getConnectedClients: () => [{ userId: 1, name: "Alice" }],
            },
        },
    });
    await mountCollaborativeStatusComponent(env);

    const fixture = getFixture();

    expect(fixture.querySelector(".o_spreadsheet_sync_status")).toHaveText("Saving");
    expect(fixture.querySelector(".o_spreadsheet_number_users")).toHaveText("1");
    expect(fixture.querySelector(".o_spreadsheet_number_users i.fa")).toHaveClass("fa-user");
});

test("synchronized", async function () {
    const env = await makeMockEnv({
        model: {
            getters: {
                isFullySynchronized: () => true,
                getConnectedClients: () => [{ userId: 1, name: "Alice" }],
            },
        },
    });
    await mountCollaborativeStatusComponent(env);

    const fixture = getFixture();

    expect(fixture.querySelector(".o_spreadsheet_sync_status")).toHaveText("Saved");
});

test("more than one user", async function () {
    const env = await makeMockEnv({
        model: {
            getters: {
                isFullySynchronized: () => true,
                getConnectedClients: () => [
                    { userId: 1, name: "Alice" },
                    { userId: 2, name: "Bob" },
                ],
            },
        },
    });
    await mountCollaborativeStatusComponent(env);

    const fixture = getFixture();

    expect(fixture.querySelector(".o_spreadsheet_number_users")).toHaveText("2");
    expect(fixture.querySelector(".o_spreadsheet_number_users i.fa")).toHaveClass("fa-users");
});
