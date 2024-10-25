import { testMailModels } from "@test_mail/../tests/test_mail_test_helpers";
import { MailTestSimpleMainAttachment } from "@test_mail_enterprise/../tests/mock_server/models/mail_test_simple_main_attachment";
import { defineModels } from "@web/../tests/web_test_helpers";

export const testMailEnterprisetModels = {
    ...testMailModels,
    MailTestSimpleMainAttachment,
};

export function defineTestMailEnterpriseModels() {
    defineModels(testMailEnterprisetModels);
}
