# Verify packed matrix hex for selected subgroup representatives.

if not IsBound(SCRIPT_DIR) then Error("SCRIPT_DIR must be bound"); fi;
if not IsBound(RUN_DIR) then Error("RUN_DIR must be bound"); fi;
if not IsBound(EXPECTED_PATH) then Error("EXPECTED_PATH must be bound"); fi;
if not IsBound(DIM) then DIM := 8; fi;
if not IsBound(USE_SMALL_GENERATING_SET) then USE_SMALL_GENERATING_SET := false; fi;

Read(Concatenation(SCRIPT_DIR, "/sp8_common.g"));
Read(EXPECTED_PATH);

ctx := SP8_BuildContext(DIM);;
P := ctx.P;;

for item in SP8_EXPECTED_MATRIX_HEX do
    rep_id := item[1];;
    expected_hex := item[2];;
    expected_order := item[3];;
    expected_generator_count := item[4];;
    H := SP8_LoadRepFromRun(P, RUN_DIR, rep_id);;
    mats := SP8_PreimageMatrixGenerators(ctx, H, USE_SMALL_GENERATING_SET);;
    actual_hex := SP8_MatrixGeneratorHexString(mats);;
    if actual_hex <> expected_hex then
        Error(Concatenation("matrix hex mismatch for rep ", String(rep_id)));
    fi;
    if Order(H) <> expected_order then
        Error(Concatenation("order mismatch for rep ", String(rep_id)));
    fi;
    if Length(mats) <> expected_generator_count then
        Error(Concatenation("generator-count mismatch for rep ", String(rep_id)));
    fi;
    if Length(mats) = 0 then
        K := Group(One(ctx.G));;
    else
        K := Group(mats);;
    fi;
    image := Image(ctx.phi, K);;
    if image <> H then
        Error(Concatenation("matrix subgroup image mismatch for rep ", String(rep_id)));
    fi;
od;

Print("verified ", Length(SP8_EXPECTED_MATRIX_HEX), " representatives\n");
QUIT_GAP(0);
