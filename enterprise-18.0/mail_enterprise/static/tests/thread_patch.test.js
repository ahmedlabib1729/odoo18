import {
    contains,
    defineMailModels,
    openFormView,
    patchUiSize,
    scroll,
    SIZES,
    start,
    startServer,
} from "@mail/../tests/mail_test_helpers";
import { describe, expect, test } from "@odoo/hoot";

describe.current.tags("desktop");
defineMailModels();

test("message list desc order", async () => {
    const pyEnv = await startServer();
    const partnerId = pyEnv["res.partner"].create({ name: "partner 1" });
    for (let i = 0; i <= 60; i++) {
        pyEnv["mail.message"].create({
            body: "not empty",
            model: "res.partner",
            res_id: partnerId,
        });
    }
    patchUiSize({ size: SIZES.XXL });
    await start();
    await openFormView("res.partner", partnerId);
    expect($(".o-mail-Message").prevAll("button:contains(Load More)")[0]).toBe(undefined, {
        message: "load more link should NOT be before messages",
    });
    expect($("button:contains(Load More)").nextAll(".o-mail-Message")[0]).toBe(undefined, {
        message: "load more link should be after messages",
    });
    await contains(".o-mail-Message", { count: 30 });
    await scroll(".o-mail-Chatter", "bottom");
    await contains(".o-mail-Message", { count: 60 });
    await scroll(".o-mail-Chatter", 0);
    // weak test, no guaranteed that we waited long enough for potential extra messages to be loaded
    await contains(".o-mail-Message", { count: 60 });
});
