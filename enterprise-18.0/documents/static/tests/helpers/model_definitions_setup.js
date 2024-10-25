/** @odoo-module **/

import { addModelNamesToFetch } from '@bus/../tests/helpers/model_definitions_helpers';

addModelNamesToFetch([
    'documents.document', 'documents.tag', 'mail.alias', 'ir.actions.server', 'ir.embedded.actions',
]);
