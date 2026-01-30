/** @odoo-module */

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, xml } from "@odoo/owl";

export class PanicGauge extends Component {
    // I inherit the standard properties of an Odoo field to integrate seamlessly with the form view.
    static props = { ...standardFieldProps };

    // I define the XML template path that renders this component.
    static template = "industrial_asset_guardian.PanicGauge";

    // I calculate the percentage value, clamping it between 0 and 100 to avoid visual errors.
    get percentage() {
        return Math.min(Math.max(this.props.record.data[this.props.name], 0), 100);
    }

    // I determine the visual color class based on the severity of the value.
    get colorClass() {
        const val = this.percentage;
        if (val >= 90) return "text-danger"; // Critical
        if (val >= 70) return "text-warning"; // Warning
        return "text-success"; // Safe
    }

    // I apply the specialized shake animation class if the value reaches critical levels (>= 90).
    // This provides immediate visual feedback to the user.
    get vibrationClass() {
        return this.percentage >= 90 ? "iag-shake-effect" : "";
    }
}

// I register this component in the fields category so it can be used in XML views via widget='panic_gauge'.
export const panicGauge = {
    component: PanicGauge,
};

registry.category("fields").add("panic_gauge", panicGauge);
