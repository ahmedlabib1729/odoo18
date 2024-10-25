import { beforeEach, describe, expect, test } from "@odoo/hoot";
import { EventBus } from "@odoo/owl";
import { defineSpreadsheetModels } from "@spreadsheet/../tests/helpers/data";
import { makeSpreadsheetMockEnv } from "@spreadsheet/../tests/helpers/model";
import { SpreadsheetCollaborativeChannel } from "@spreadsheet_edition/bundle/o_spreadsheet/collaborative/spreadsheet_collaborative_channel";
import { mockService } from "@web/../tests/web_test_helpers";

describe.current.tags("headless");
defineSpreadsheetModels();

let env;

beforeEach(async () => {
    const channels = [];
    const _bus = new EventBus();

    const busService = {
        addChannel: (name) => {
            channels.push(name);
        },
        subscribe: (eventName, handler) => {
            _bus.addEventListener("notif", ({ detail }) => {
                if (detail.type === eventName) {
                    handler(detail.payload, { id: detail.id });
                }
            });
        },
        notify: (message) => {
            _bus.trigger("notif", message);
        },
    };
    const rpc = function (route, params) {
        // Mock the server behavior: new revisions are pushed in the bus
        if (params.method === "dispatch_spreadsheet_message") {
            const [documentId, message] = params.args;
            busService.notify({ type: "spreadsheet", payload: { id: documentId, message } });
            return true;
        }
    };
    mockService("bus_service", busService);
    env = await makeSpreadsheetMockEnv({
        mockRPC: rpc,
    });
});

test("sending a message forward it to the registered listener", async function () {
    const channel = new SpreadsheetCollaborativeChannel(env, "my.model", 5);
    let i = 5;
    channel.onNewMessage("anId", (message) => {
        expect.step("message");
        expect(message.message).toBe("hello", {
            message: "It should have the correct message content",
        });
        i = 8;
    });
    await channel.sendMessage("hello");
    expect(i).toBe(8);
    // It should have received the message
    expect.verifySteps(["message"]);
});

test("previous messages are forwarded when registering a listener", async function () {
    const channel = new SpreadsheetCollaborativeChannel(env, "my.model", 5);
    await channel.sendMessage("hello");
    channel.onNewMessage("anId", (message) => {
        expect.step("message");
        expect(message.message).toBe("hello", {
            message: "It should have the correct message content",
        });
    });
    // It should have received the pending message
    expect.verifySteps(["message"]);
});

test("the channel does not care about other bus messages", function () {
    const channel = new SpreadsheetCollaborativeChannel(env, "my.model", 5);
    channel.onNewMessage("anId", () => expect.step("message"));
    env.services.bus_service.notify("a-random-channel", "a-random-message");
    // The message should not have been received
    expect.verifySteps([]);
});
