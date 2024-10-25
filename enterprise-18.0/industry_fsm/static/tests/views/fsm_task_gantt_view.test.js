import { describe, expect, test } from "@odoo/hoot";
import { animationFrame, mockDate } from "@odoo/hoot-mock";
import { click } from "@odoo/hoot-dom";

import { onRpc, mountView } from "@web/../tests/web_test_helpers";

import { defineProjectModels, projectModels } from "@project/../tests/project_models";

describe.current.tags("desktop");
defineProjectModels();

const { ProjectTask } = projectModels;

test("fsm task gantt view", async () => {
    mockDate("2024-01-03 07:00:00");
    onRpc("get_all_deadlines", () => ({ milestone_id: [], project_id: [] }));

    ProjectTask._records = [
        {
            id: 1,
            planned_date_begin: "2024-01-10 06:30:00",
            date_deadline: "2024-01-10 11:30:00",
        },
        {
            id: 2,
            planned_date_begin: "2024-01-01 06:00:00",
            date_deadline: "2024-01-01 12:30:00",
        },
    ];

    ProjectTask._views = {
        form: `
            <form>
                <field name="name"/>
                <field name="planned_date_begin"/>
                <field name="date_deadline"/>
            </form>
        `,
    };

    const now = luxon.DateTime.now();

    await mountView({
        resModel: "project.task",
        arch: '<gantt date_start="planned_date_begin" date_stop="date_deadline" js_class="task_gantt" />',
        type: "gantt",
        context: { fsm_mode: true },
    });

    expect(".o_gantt_view").toHaveCount(1);
    expect(".modal").toHaveCount(0);
    await click(".o_gantt_button_add.btn-primary");
    await animationFrame();
    expect(".modal").toHaveCount(1);
    expect(".modal .o_field_widget[name=planned_date_begin] .o_input").toHaveValue(
        now.toFormat("MM/dd/yyyy 00:00:00"),
        {
            message:
                "The fsm_mode present in the view context should set the start_datetime to the current day instead of the first day of the gantt view",
        }
    );
});
