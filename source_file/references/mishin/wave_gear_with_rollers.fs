FeatureScript 2399;
import(path : "onshape/std/common.fs", version : "2399.0");
import(path : "onshape/std/geometry.fs", version : "2399.0");
icon::import(path : "046933af527dd557528f6f9b", version : "0e478941b3c189f428a22410");

const SEPARATOR_WALL_HEIGHT = 2 * millimeter;

annotation { "Feature Type Name" : "Roller Wave Gear", "Editing Logic Function" : "editWaveRollerDriveLogic", "Icon" : icon::BLOB_DATA }

export const rollerWave = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {

        annotation { "Name" : "Roller diameter" }
        isLength(definition.rollerDiameter, ROLLER_DIAM_BOUNDS);
        annotation { "Name" : "Rollers number" }
        isInteger(definition.nRol, ROLLERS_NUMBER_BOUNDS);

        annotation { "Name" : "Use balls" }
        definition.isBalls is boolean;

        annotation { "Name" : "Roller height" }
        isLength(definition.rollerHeight, ROLLER_DIAM_BOUNDS);


        annotation { "Name" : "Bearing inner diameter" }
        isLength(definition.bearingIn, BEARING_INNER_BOUNDS);

        annotation { "Name" : "Bearing outer diameter" }
        isLength(definition.bearingOut, BEARING_OUTER_BOUNDS);

        annotation { "Name" : "Bearing height" }
        isLength(definition.bearingH, BEARING_HEIGHT_BOUNDS);

        annotation { "Name" : "Use minimal cycloid diameter" }
        definition.useMinCycloidDia is boolean;

        annotation { "Name" : "Cycloid outer diameter" }
        isLength(definition.cycloidOuterDiameter, CYCL_OUTER_DIAM_BOUNDS);

        annotation { "Name" : "Body diameter" }
        isLength(definition.outerDiameter, OUTER_DIAM_BOUNDS);

        annotation { "Name" : "Add bearing housing lip" }
        definition.addBearingLip is boolean;

        // annotation { "Name" : "Thickness of gear" }
        // isLength(definition.thickness, THICKNESS_BOUNDS);

        annotation { "Name" : "Cover the separator" }
        definition.coverSeparator is boolean;

        annotation { "Name" : "Input shaft diameter" }
        isLength(definition.inputShaftDia, INPUT_SHAFT_DIA_BOUNDS);

        annotation { "Name" : "Parts offset" }
        isLength(definition.partsOffset, PARTS_OFFSET_BOUNDS);

        annotation { "Name" : "Roller tolerance" }
        isLength(definition.rollerTolerance, ROLLER_TOLERANCE_BOUNDS);

        annotation { "Name" : "Sketch origin point", "Filter" : EntityType.VERTEX, "MaxNumberOfPicks" : 1 }
        definition.sketchOrigin is Query;

    }
    {
        var props = prepareProperties(definition);

        var everything = evaluateQuery(context, qEverything(EntityType.BODY)); // Capture state before feature actions

        ringGear(context, id, props);
        outputShaft(context, id, props);
        waveGenerator(context, id, props);
        inputShaft(context, id, props);
        // rollers(context, id, props);

        if (evaluateQuery(context, definition.sketchOrigin) != [])
        {
            // Transform to the sketch origin
            performTransform(context, id, {
                        "entities" : qSubtraction(qUnion(evaluateQuery(context, qEverything(EntityType.BODY))), qUnion(everything)),
                        "center" : definition.sketchOrigin
                    });
        }
    });


function prepareProperties(definition)
{
    var dRol = definition.rollerDiameter; // Roller diameter;
    var rRol = dRol / 2; // Roller radius;

    var cyMod = 0.2; // Cycloidal Modulus;
    var eC = cyMod * dRol; // Eccentricity;

    var nRol = definition.nRol; // Rollers number;
    var nCav = nRol + 1; // Cavities number (number of waves/holes);

    var rInOfBearingEcc = definition.bearingOut / 2 + dRol - eC;

    var rInMin = max(
    // Of minimal Cycloid rounded
    ceil((1.03 * dRol.value) / sin((PI / nCav) * radian) * 10000) / 10000 * meter,
    // Of bearing
    rInOfBearingEcc
    );

    var cycloidOuterDiameter = definition.cycloidOuterDiameter;
    var outerDiameter = definition.outerDiameter;
    var rollerHeight = definition.rollerHeight;

    // Minimal thickness
    var thickness = 1 * millimeter; // definition.thickness;

    if (rInMin > (cycloidOuterDiameter / 2 - 2 * eC) || definition.useMinCycloidDia)
    {
        var minDia = (rInMin.value + 2 * eC.value) * 2;
        cycloidOuterDiameter = minDia * meter;
    }


    var minBodyThickness = 4 * millimeter;

    if (outerDiameter <= cycloidOuterDiameter + minBodyThickness)
    {
        outerDiameter = cycloidOuterDiameter + minBodyThickness;
    }

    if (definition.isBalls)
    {
        rollerHeight = definition.rollerDiameter;
    }

    var minHByRoller = rollerHeight + definition.rollerTolerance + SEPARATOR_WALL_HEIGHT * 2 + definition.partsOffset * 4;

    var minHByBearing = definition.bearingH
    + (definition.coverSeparator ? SEPARATOR_WALL_HEIGHT + definition.partsOffset : 0 * millimeter)
    + definition.partsOffset * (definition.addBearingLip ? 3 : 2);

    var minH = max(
    minHByRoller,
    minHByBearing
    );

    if (thickness <= minH)
    {
        thickness = minH;
    }

    var rOut = cycloidOuterDiameter / 2; // Radius of main cycloid;
    var rIn = rOut - 2 * eC; // Inner radius of cycloid;
    var rEcc = rIn + eC - dRol; // Radius of Eccentric Wheel

    return {
            "dRol" : dRol * meter,
            "rRol" : rRol * meter,

            "isBalls" : definition.isBalls,

            "eC" : eC * meter,

            "nRol" : nRol,
            "nCav" : nCav,

            "rOut" : rOut * meter,
            "rIn" : rIn * meter,

            "rInMin" : rInMin * meter,

            "rEcc" : rEcc,

            "bearingIn" : definition.bearingIn,
            "bearingOut" : definition.bearingOut,
            "bearingH" : definition.bearingH,
            "addBearingLip" : definition.addBearingLip,

            "skOrigin" : definition.sketchOrigin,

            "outerDiameter" : outerDiameter,
            "cycloidOuterDiameter" : cycloidOuterDiameter,
            "rollerHeight" : rollerHeight,
            "thickness" : thickness,

            "coverSeparator" : definition.coverSeparator,

            "inputShaftDia" : definition.inputShaftDia,
            "partsOffset" : definition.partsOffset,
            "rollerTolerance" : definition.rollerTolerance
        };
}

// Separator
function outputShaft(context is Context, id is Id, definition is map)
{

    var rEcc = definition.rEcc.value;
    var rRol = definition.rRol.value;

    var eC = definition.eC.value;

    var nRol = definition.nRol;

    var hRol = definition.rollerHeight.value;
    var rolTol = definition.rollerTolerance.value / 2;
    var isBalls = definition.isBalls;

    var sepWidth = 2.2 * eC;

    var rSepM = rEcc + rRol;
    var rSepOut = rSepM + sepWidth / 2;
    var rSepIn = rSepM - sepWidth / 2;

    var coverSeparator = definition.coverSeparator;

    assignVariable(context, id + "variable_separatorInnerDia", {
                "mode" : VariableMode.ASSIGNED,
                "name" : "separatorInnerDia",
                "variableType" : VariableType.LENGTH,
                "lengthValue" : rSepIn * meter * 2,
                "measurementMode" : VariableMeasurementMode.DISTANCE,
            });

    assignVariable(context, id + "variable_separatorOuterDia", {
                "mode" : VariableMode.ASSIGNED,
                "name" : "separatorOuterDia",
                "variableType" : VariableType.LENGTH,
                "lengthValue" : rSepOut * meter * 2,
                "measurementMode" : VariableMeasurementMode.DISTANCE,
            });

    var separatorSketch = newSketch(context, id + "sketch_outputShaft", {
            "sketchPlane" : qCreatedBy(makeId("Top"), EntityType.FACE)
        });

    var outHeight = definition.thickness;

    skCircle(separatorSketch, "separatorOut", {
                "center" : vector(0, 0) * meter,
                "radius" : rSepOut * meter
            });

    skCircle(separatorSketch, "separatorOin", {
                "center" : vector(0, 0) * meter,
                "radius" : rSepIn * meter
            });

    skSolve(separatorSketch);

    opExtrude(context, id + "extrude_outputShaft", {
                "entities" : qSketchRegion(id + "sketch_outputShaft", true),
                "direction" : vector(0, 0, 1),
                "endBound" : BoundingType.BLIND,
                "endDepth" : outHeight - definition.partsOffset,

                "startBound" : BoundingType.BLIND,
                "startDepth" : -definition.partsOffset,
            // "startTranslationalOffset": definition.partsOffset,
            });


    // Hole
    var holeSketch = newSketch(context, id + "sketch_outputShaftHole", {
            "sketchPlane" : qCreatedBy(makeId("Front"), EntityType.FACE)
        });

    var centerPointY = definition.thickness.value / 2;

    if (isBalls)
    {
        skCircle(holeSketch, "shaftHole", {
                    "center" : vector(0, centerPointY) * meter,
                    "radius" : rRol * meter
                });
    }
    else
    {
        skRectangle(holeSketch, "shaftHole", {
                    "firstCorner" : vector(-(rRol + rolTol), centerPointY - (hRol / 2 + rolTol)) * meter,
                    "secondCorner" : vector(rRol + rolTol, centerPointY + (hRol / 2 + rolTol)) * meter
                });
    }

    skSolve(holeSketch);

    opExtrude(context, id + "extrude_outputShaftHole", {
                "entities" : qSketchRegion(id + "sketch_outputShaftHole", true),
                "direction" : vector(0, 1, 0),
                "endBound" : BoundingType.BLIND,
                "endDepth" : definition.rOut,
            });

    opBoolean(context, id + "subtract_outputShaftHole", {
                "targets" : qCreatedBy(id + "extrude_outputShaft", EntityType.BODY),
                "tools" : qCreatedBy(id + "extrude_outputShaftHole", EntityType.BODY),
                "operationType" : BooleanOperationType.SUBTRACTION
            });

    // SPECIAL FOR AXIS
    var patternSketch = newSketch(context, id + "sketch_patternAxis", {
            "sketchPlane" : qCreatedBy(makeId("Top"), EntityType.FACE)
        });
    skCircle(patternSketch, "separatorPatternAxis", {
                "center" : vector(0, 0) * meter,
                "radius" : rSepOut * meter,
                "construction" : true,
            });
    skSolve(patternSketch);


    circularPattern(context, id + "circular_holes", {
                "patternType" : PatternType.FACE,
                "faces" : qCreatedBy(id + "subtract_outputShaftHole", EntityType.FACE),
                "axis" : qCreatedBy(id + "sketch_patternAxis", EntityType.EDGE),
                "angle" : 360 * degree,
                "instanceCount" : nRol,
                "equalSpace" : true
            });

    opDeleteBodies(context, id + "deleteBodies_outputShaft", {
                "entities" : qUnion([qCreatedBy(id + "sketch_outputShaftHole"), qCreatedBy(id + "sketch_patternAxis")])
            });

    // Cover Separator
    if (coverSeparator)
    {
        var coverSeparatorSketch = newSketch(context, id + "sketch_outputShaftCover", {
                "sketchPlane" : qCreatedBy(makeId("Top"), EntityType.FACE)
            });

        skCircle(coverSeparatorSketch, "coverSeparatorOut", {
                    "center" : vector(0, 0) * meter,
                    "radius" : rSepOut * meter
                });

        skCircle(coverSeparatorSketch, "coverSeparatorInputShaftHole", {
                    "center" : vector(0, 0) * meter,
                    "radius" : (definition.inputShaftDia + 1 * millimeter) / 2
                });

        skSolve(coverSeparatorSketch);

        opExtrude(context, id + "extrude_outputShaftCover", {
                    "entities" : qSketchRegion(id + "sketch_outputShaftCover", true),
                    "direction" : vector(0, 0, 1),
                    "endBound" : BoundingType.BLIND,
                    "endDepth" : outHeight - definition.partsOffset,
                    // SEPARATOR_WALL_HEIGHT + definition.partsOffset,

                    "startBound" : BoundingType.BLIND,
                    "startDepth" : -outHeight + definition.partsOffset + SEPARATOR_WALL_HEIGHT,
                // -definition.partsOffset,
                // "startTranslationalOffset": definition.partsOffset,
                });

        opBoolean(context, id + "union_outputShaft", {
                    "tools" : qUnion([qCreatedBy(id + "extrude_outputShaft", EntityType.BODY), qCreatedBy(id + "extrude_outputShaftCover", EntityType.BODY)]),
                    "operationType" : BooleanOperationType.UNION
                });

        opDeleteBodies(context, id + "deleteEnclosureSketches", {
                    "entities" : qUnion([qCreatedBy(id + "sketch_outputShaftCover")])
                });
    }

    setProperty(context, {
                "entities" : qCreatedBy(id + "extrude_outputShaft", EntityType.BODY),
                "propertyType" : PropertyType.NAME,
                "value" : "Separator (Output Shaft)"
            });
}


function waveGenerator(context is Context, id is Id, definition is map)
{
    var rEcc = definition.rEcc.value;
    var bearingOut = definition.bearingOut.value;
    var eC = definition.eC.value;
    var center = vector(0, eC) * meter;

    assignVariable(context, id + "variable_waveGeneratorDia", {
                "mode" : VariableMode.ASSIGNED,
                "name" : "waveGeneratorDia",
                "variableType" : VariableType.LENGTH,
                "lengthValue" : definition.rEcc * 2,
                "measurementMode" : VariableMeasurementMode.DISTANCE,
            });

    var waveGeneratorSketch = newSketch(context, id + ("sketch_waveGenerator"), {
            "sketchPlane" : qCreatedBy(makeId("Top"), EntityType.FACE)
        });

    skCircle(waveGeneratorSketch, "waveGenerator", {
                "center" : center,
                "radius" : rEcc * meter
            });

    if (round(rEcc * 1000000) == round(bearingOut / 2 * 1000000))
    {
        skSolve(waveGeneratorSketch);
        return;
    }

    var startDepth = -definition.partsOffset;
    var endDepth = definition.thickness - (definition.coverSeparator ? definition.partsOffset * 2 + SEPARATOR_WALL_HEIGHT : definition.partsOffset);

    skCircle(waveGeneratorSketch, "waveGeneratorBearing", {
                "center" : center,
                "radius" : bearingOut / 2 * meter
            });

    skSolve(waveGeneratorSketch);

    opExtrude(context, id + ("extrude_waveGenerator"), {
                "entities" : qSketchRegion(id + ("sketch_waveGenerator"), true),
                "direction" : vector(0, 0, 1),
                "endBound" : BoundingType.BLIND,
                "endDepth" : endDepth,

                "startBound" : BoundingType.BLIND,
                "startDepth" : startDepth
            });


    // Bearing housing lip
    if (definition.addBearingLip)
    {
        var outerBearingLipSketch = newSketch(context, id + "sketch_outerBearingLip", {
                "sketchPlane" : qCreatedBy(makeId("Top"), EntityType.FACE)
            });

        skCircle(outerBearingLipSketch, "outerBearingSize", {
                    "center" : center,
                    "radius" : bearingOut / 2 * meter
                });

        skCircle(outerBearingLipSketch, "outerBearingLip", {
                    "center" : center,
                    "radius" : bearingOut / 2 * meter - 1 * millimeter
                });

        skSolve(outerBearingLipSketch);

        opExtrude(context, id + "extrude_outerBearingLip", {
                    "entities" : qSketchRegion(id + "sketch_outerBearingLip", true),
                    "direction" : vector(0, 0, 1),
                    "endBound" : BoundingType.BLIND,
                    "endDepth" : endDepth - max(definition.bearingH, definition.bearingH + (definition.rollerHeight - definition.bearingH) / 2),

                    "startBound" : BoundingType.BLIND,
                    "startDepth" : startDepth,
                });

        opBoolean(context, id + "boolean_outerBearingLip", {
                    "tools" : qUnion([qCreatedBy(id + "extrude_waveGenerator", EntityType.BODY), qCreatedBy(id + "extrude_outerBearingLip", EntityType.BODY)]),
                    "operationType" : BooleanOperationType.UNION
                });


        opDeleteBodies(context, id + "deleteWaveGeneratorSketches", {
                    "entities" : qUnion([qCreatedBy(id + "sketch_outerBearingLip")])
                });
    }

    setProperty(context, {
                "entities" : qCreatedBy(id + "extrude_waveGenerator", EntityType.BODY),
                "propertyType" : PropertyType.NAME,
                "value" : "Wave Generator"
            });
}

function inputShaft(context is Context, id is Id, definition is map)
{
    var bearingIn = definition.bearingIn.value;
    var eC = definition.eC.value;

    var center = vector(0, eC) * meter;

    // var startDepth = definition.coverSeparator ? -definition.partsOffset * 2 - SEPARATOR_WALL_HEIGHT : -definition.partsOffset;
    // var endDepth = definition.thickness - definition.partsOffset;

    var startDepth = -definition.partsOffset;
    var endDepth = definition.thickness - (definition.coverSeparator ? definition.partsOffset * 2 + SEPARATOR_WALL_HEIGHT : definition.partsOffset);


    var inputShaftSketch = newSketch(context, id + "sketch_inputShaft", {
            "sketchPlane" : qCreatedBy(makeId("Top"), EntityType.FACE)
        });

    skCircle(inputShaftSketch, "inputShaft", {
                "center" : center,
                "radius" : bearingIn / 2 * meter
            });

    skSolve(inputShaftSketch);

    opExtrude(context, id + "extrude_inputShaft", {
                "entities" : qSketchRegion(id + "sketch_inputShaft", true),
                "direction" : vector(0, 0, 1),
                "endBound" : BoundingType.BLIND,
                "endDepth" : endDepth,

                "startBound" : BoundingType.BLIND,
                "startDepth" : startDepth,
            });

    // Bearing housing lip
    if (definition.addBearingLip)
    {
        var innerBearingLipSketch = newSketch(context, id + "sketch_innerBearingLip", {
                "sketchPlane" : qCreatedBy(makeId("Top"), EntityType.FACE)
            });

        skCircle(innerBearingLipSketch, "innerBearingLip", {
                    "center" : center,
                    "radius" : bearingIn / 2 * meter + 1 * millimeter
                });

        skSolve(innerBearingLipSketch);

        opExtrude(context, id + "extrude_innerBearingLip", {
                    "entities" : qSketchRegion(id + "sketch_innerBearingLip", true),
                    "direction" : vector(0, 0, 1),
                    "endBound" : BoundingType.BLIND,
                    "endDepth" : endDepth - max(definition.bearingH, definition.bearingH + (definition.rollerHeight - definition.bearingH) / 2),

                    "startBound" : BoundingType.BLIND,
                    "startDepth" : startDepth,
                });

        opBoolean(context, id + "boolean_innerBearingLip", {
                    "tools" : qUnion([qCreatedBy(id + "extrude_inputShaft", EntityType.BODY), qCreatedBy(id + "extrude_innerBearingLip", EntityType.BODY)]),
                    "operationType" : BooleanOperationType.UNION
                });
    }

    // Shaft hole
    var shaftHoleSketch = newSketch(context, id + "sketch_shaftHole", {
            "sketchPlane" : qCreatedBy(makeId("Top"), EntityType.FACE)
        });

    skCircle(shaftHoleSketch, "shaftHole", {
                "center" : vector(0, 0) * meter,
                "radius" : definition.inputShaftDia / 2
            });

    skSolve(shaftHoleSketch);

    opExtrude(context, id + "extrude_shaftHole", {
                "entities" : qSketchRegion(id + "sketch_shaftHole", true),
                "direction" : vector(0, 0, 1),
                "endBound" : BoundingType.BLIND,
                "endDepth" : definition.thickness,
            });

    opBoolean(context, id + "boolean_shaftHole", {
                "tools" : qCreatedBy(id + "extrude_shaftHole", EntityType.BODY),
                "targets" : qCreatedBy(id + "extrude_inputShaft", EntityType.BODY),
                "operationType" : BooleanOperationType.SUBTRACTION
            });

    // Cleanup
    opDeleteBodies(context, id + "deleteInputShaftSketches", {
                "entities" : qUnion([
                        qCreatedBy(id + "sketch_innerBearingLip"),
                        qCreatedBy(id + "sketch_shaftHole"),
                    // qCreatedBy(id + "sketch_inputShaft")
                    ])
            });

    setProperty(context, {
                "entities" : qCreatedBy(id + "extrude_inputShaft", EntityType.BODY),
                "propertyType" : PropertyType.NAME,
                "value" : "Eccentric Cam (Input shaft)"
            });
}



// function rollers(context is Context, id is Id, definition is map)
// {
//     var rRol = definition.rRol.value;
//     var rOut = definition.rOut.value;
//     var rEcc = definition.rEcc.value;

//     var eC = definition.eC.value;

//     var nRol = definition.nRol;
//     var nCav = definition.nCav;

//     // Sketch
//     var rRolAxis = rOut - rRol;
//     var rollersSketch = newSketch(context, id + "rollers", {
//             "sketchPlane" : qCreatedBy(makeId("Top"), EntityType.FACE)
//         });

//     var R = rOut - eC;

//     var theta = 0 * radian;
//     var x = 0;
//     var y = 0;

//     for (var i = 0; i < nRol; i += 1)
//     {
//         theta = (i / nRol) * 2 * PI * radian;

//         var sRol = sqrt(
//         (rRol + rEcc) ^ 2 - (eC * sin(nCav * theta)) ^ 2
//         );

//         var lRol = eC * cos(nCav * theta) + sRol;

//         x = lRol * sin(theta);
//         y = lRol * cos(theta);

//         skCircle(rollersSketch, "roller_" ~ i, {
//                     "center" : vector(x, y) * meter,
//                     "radius" : rRol * meter
//                 });
//     }
//     skSolve(rollersSketch);
// }


function ringGear(context is Context, id is Id, definition is map)
{
    var rOut = definition.rOut.value;
    var rOutCase = definition.outerDiameter.value / 2;

    assignVariable(context, id + "variable_cycloidOutDia", {
                "mode" : VariableMode.ASSIGNED,
                "name" : "cycloidOutDia",
                "variableType" : VariableType.LENGTH,
                "lengthValue" : rOut * meter * 2,
                "measurementMode" : VariableMeasurementMode.DISTANCE,
            });

    var cycloidPoints = plotCycloid(context, id, definition);

    var cycloidSketch = newSketch(context, id + "sketch_Cycloid", {
            "sketchPlane" : qCreatedBy(makeId("Top"), EntityType.FACE)
        });

    skFitSpline(cycloidSketch, "spline1", {
                "points" : cycloidPoints
            });

    skCircle(cycloidSketch, "circle_base", {
                "center" : vector(0, 0) * meter,
                "radius" : rOut * meter,
                "construction" : true,
            });

    skCircle(cycloidSketch, "outer_circle", {
                "center" : vector(0, 0) * meter,
                "radius" : rOutCase * meter
            });

    skSolve(cycloidSketch);

    opExtrude(context, id + "extrude_Cycloid", {
                "entities" : qSketchRegion(id + "sketch_Cycloid", true),
                "direction" : vector(0, 0, 1),
                "endBound" : BoundingType.BLIND,
                "endDepth" : definition.thickness
            });

    // Delete points from sketch
    opDeleteBodies(context, id + "deleteBodies1", {
                "entities" : qUnion([qCreatedBy(id + "sketch_Cycloid", EntityType.VERTEX)])
            });

    setProperty(context, {
                "entities" : qCreatedBy(id + "extrude_Cycloid", EntityType.BODY),
                "propertyType" : PropertyType.NAME,
                "value" : "Body (Inner Cycloid Ring Gear)"
            });
}

export function plotCycloid(context is Context, id is Id, definition is map)
{
    var eC = definition.eC.value;

    var rRol = definition.rRol.value;
    var rEcc = definition.rEcc.value;

    var nRol = definition.nRol;
    var nCav = definition.nCav;

    var res = nRol * 20;

    var theta = 0 * radian;
    var x = 0;
    var y = 0;

    var points = [];


    for (var i = 0; i < res; i += 1)
    {
        theta = (i / res) * 2 * PI * radian;

        var sRol = sqrt(
        (rRol + rEcc) ^ 2 - (eC * sin(nCav * theta)) ^ 2
        );
        var lRol = eC * cos(nCav * theta) + sRol;
        var Xi = atan2(eC * nCav * sin(nCav * theta), sRol);

        x = lRol * sin(theta) + rRol * sin(theta + Xi);
        y = lRol * cos(theta) + rRol * cos(theta + Xi);

        points = append(points, vector(x, y) * meter);
    }
    points = append(points, points[0]);

    return points;
}

function performTransform(context is Context, id is Id, definition)
{
    const newCoordSys = coordSystem(
        evVertexPoint(context, {
                    "vertex" : definition.center
                }),
        evOwnerSketchPlane(context, {
                        "entity" : definition.center
                    }).x,
        evOwnerSketchPlane(context, {
                        "entity" : definition.center
                    }).normal
        );

    const finalTransform = toWorld(newCoordSys);

    opTransform(context, id + "transformFinal", {
                "bodies" : definition.entities,
                "transform" : finalTransform
            });
}

export function editWaveRollerDriveLogic(context is Context, id is Id, oldDefinition is map, definition is map, isCreating is boolean, specifiedParameters is map, hiddenBodies is Query) returns map
{
    if (isCreating)
    {
        definition.useMinCycloidDia = true;
        definition.outerDiameter = 50 * millimeter;
    }

    var props = prepareProperties(definition);

    if (definition.outerDiameter != props.outerDiameter)
        definition.outerDiameter = props.outerDiameter;

    if (definition.cycloidOuterDiameter != props.cycloidOuterDiameter)
        definition.cycloidOuterDiameter = props.cycloidOuterDiameter;

    // if (definition.rollerHeight != props.rollerHeight)
    //     definition.rollerHeight = props.rollerHeight;

    // if (definition.thickness != props.thickness)
    //     definition.thickness = props.thickness;

    return definition;
}


const ROLLER_DIAM_BOUNDS =
{
            (meter) : [1e-5, 0.006, 500],
            (centimeter) : .6,
            (millimeter) : 6.0,
            (inch) : 0.23
        } as LengthBoundSpec;

const CYCL_OUTER_DIAM_BOUNDS =
{
            (meter) : [1e-5, 0.057, 500],
            (centimeter) : 5.7,
            (millimeter) : 57.0,
            (inch) : 2.25
        } as LengthBoundSpec;

const OUTER_DIAM_BOUNDS =
{
            (meter) : [1e-5, 0.06, 500],
            (centimeter) : 6.0,
            (millimeter) : 60.0,
            (inch) : 2.36
        } as LengthBoundSpec;


const ROLLERS_NUMBER_BOUNDS =
{
            (unitless) : [3, 12, 250]
        } as IntegerBoundSpec;


const BEARING_INNER_BOUNDS =
{
            (meter) : [1e-5, 0.015, 500],
            (centimeter) : 1.5,
            (millimeter) : 15.0,
            (inch) : .6
        } as LengthBoundSpec;

const BEARING_OUTER_BOUNDS =
{
            (meter) : [1e-5, 0.025, 500],
            (centimeter) : 2.5,
            (millimeter) : 25.0,
            (inch) : 1
        } as LengthBoundSpec;

const BEARING_HEIGHT_BOUNDS =
{
            (meter) : [1e-5, 0.006, 500],
            (centimeter) : 0.6,
            (millimeter) : 6.0,
            (inch) : .23
        } as LengthBoundSpec;

// const THICKNESS_BOUNDS =
// {
//             (meter) : [1e-5, 0.01, 500],
//             (centimeter) : 1,
//             (millimeter) : 10.0,
//             (inch) : 0.4
//         } as LengthBoundSpec;

const INPUT_SHAFT_DIA_BOUNDS =
{
            (meter) : [1e-5, 0.005, 500],
            (centimeter) : .5,
            (millimeter) : 5.0,
            (inch) : 0.2
        } as LengthBoundSpec;


const PARTS_OFFSET_BOUNDS =
{
            (meter) : [1e-5, 0.0008, 500],
            (centimeter) : .08,
            (millimeter) : 0.8,
            (inch) : 0.031
        } as LengthBoundSpec;

const ROLLER_TOLERANCE_BOUNDS =
{
            (meter) : [1e-5, 0.0001, 500],
            (centimeter) : .01,
            (millimeter) : 0.1,
            (inch) : 0.0039
        } as LengthBoundSpec;
