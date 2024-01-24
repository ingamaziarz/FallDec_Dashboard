import React, { useState } from 'react';
import { useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * ExampleComponent is an example component.
 * It takes a property, `label`, and
 * displays it.
 * It renders an input with the property `value`
 * which is editable by the user.
 */


const Widget = (props) => {
    const { id, label, setProps, value, data} = props;
    let l0_val = null;
    let l1_val = null;
    let l2_val = null;
    let r0_val = null;
    let r1_val = null;
    let r2_val = null;
    let l0_color = 'rgba(51,85,62, 0.9)';
    let l1_color = 'rgba(109,144,120, 0.9)';
    let l2_color = 'rgba(164,193,173, 0.9)';
    let r2_color = 'rgba(165,171,237, 0.9)';
    let r1_color = 'rgba(107,116,208, 0.9)';
    let r0_color = 'rgba(55,66,181, 0.9)';
    if (data) {
        console.log(data);
        l0_val = data[0].sensor_value;
        l1_val = data[1].sensor_value;
        l2_val = data[2].sensor_value;
        r0_val = data[3].sensor_value;
        r1_val = data[4].sensor_value;
        r2_val = data[5].sensor_value;
        if (data[0].anomaly == 1)
            l0_color = 'rgba(255, 0, 0, 1)';
        if (data[1].anomaly == 1)
            l1_color = 'rgba(255, 0, 0, 1)';
        if (data[2].anomaly == 1)
            l2_color = 'rgba(255, 0, 0, 1)';
        if (data[3].anomaly == 1)
            r0_color = 'rgba(255, 0, 0, 1)';
        if (data[4].anomaly == 1)
            r1_color = 'rgba(255, 0, 0, 1)';
        if (data[5].anomaly == 1)
            r2_color = 'rgba(255, 0, 0, 1)';
                    }
    else {
        l0_val = 0;
        l1_val = 0;
        l2_val = 0;
        r0_val = 0;
        r1_val = 0;
        r2_val = 0;
    }

    // Set the image URL
    const imageUrl = "https://t3.ftcdn.net/jpg/03/28/12/78/360_F_328127854_EXZSGrEHAKngzarRHlBh9PaIOY3lgAuk.jpg";

    // Function to handle input value changes
    const handleInputChange = (e) => {
        setProps({ value: e.target.value });
    };


    // Function to calculate the center position of the red point
    const calculateSensorsPosition = () => {
        const imageContainer = document.getElementById(`${id}-imageContainer`);
        const L0 = document.getElementById(`${id}-L0`);
        const L1 = document.getElementById(`${id}-L1`);
        const L2 = document.getElementById(`${id}-L2`);
        const R0 = document.getElementById(`${id}-R0`);
        const R1 = document.getElementById(`${id}-R1`);
        const R2 = document.getElementById(`${id}-R2`);

    };

    // Run the calculation once the component is mounted
    useEffect(() => {
        calculateSensorsPosition();
    }, []);

    return (
        <div id={id}>
            <div id={`${id}-imageContainer`} style={{ position: "relative" }}>
                <img src={imageUrl} style={{ width: "23%" }}/>
                <div
                    id={`${id}-L0`}
                    style={{
                        position: "absolute",
                        width: l0_val / 50,
                        height: l0_val / 50,
                        top: "35%",
                        left: "46%",
                        backgroundColor: l0_color,
                        borderRadius: "50%",
                        transform: "translate(-50%, -50%)",
                    }}
                ></div>
                <div
                    id={`${id}-L1`}
                    style={{
                        position: "absolute",
                        width: l1_val / 50,
                        height: l1_val / 50,
                        top: "45%",
                        left: "43%",
                        backgroundColor: l1_color,
                        borderRadius: "50%",
                        transform: "translate(-50%, -50%)",
                    }}
                ></div>
                                <div
                    id={`${id}-L2`}
                    style={{
                        position: "absolute",
                        width: l2_val / 50,
                        height: l2_val / 50,
                        top: "80%",
                        left: "45%",
                        backgroundColor: l2_color,
                        borderRadius: "50%",
                        transform: "translate(-50%, -50%)",
                    }}
                ></div>
                <div
                    id={`${id}-R0`}
                    style={{
                        position: "absolute",
                        top: "35%",
                        left: "55%",
                        width: r0_val / 50,
                        height: r0_val / 50,
                        backgroundColor: r0_color,
                        borderRadius: "50%",
                        transform: "translate(-50%, -50%)",
                    }}
                ></div>
                                <div
                    id={`${id}-R1`}
                    style={{
                        position: "absolute",
                        width: r1_val / 50,
                        height: r1_val / 50,
                        top: "45%",
                        left: "58%",
                        backgroundColor: r1_color,
                        borderRadius: "50%",
                        transform: "translate(-50%, -50%)",
                    }}
                ></div>
                                <div
                    id={`${id}-R2`}
                    style={{
                        position: "absolute",
                        width: r2_val / 50,
                        height: r2_val / 50,
                        top: "80%",
                        left: "55%",
                        backgroundColor: r2_color,
                        borderRadius: "50%",
                        transform: "translate(-50%, -50%)",
                    }}
                ></div>

            </div>

        </div>
    );
};

Widget.defaultProps = {};

Widget.propTypes = {
    /**
     * The ID used to identify this component in Dash callbacks.
     */
    id: PropTypes.string,

    /**
     * A label that will be printed when this component is rendered.
     */
    label: PropTypes.string.isRequired,

    /**
     * The value displayed in the input.
     */
    value: PropTypes.string,
    data: PropTypes.array,
    /**
     * Dash-assigned callback that should be called to report property changes
     * to Dash, to make them available for callbacks.
     */
    setProps: PropTypes.func
};

export default Widget;
