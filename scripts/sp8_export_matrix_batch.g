# Export a contiguous id range of subgroup representatives as packed matrix hex.

if not IsBound(SCRIPT_DIR) then Error("SCRIPT_DIR must be bound"); fi;
if not IsBound(RUN_DIR) then Error("RUN_DIR must be bound"); fi;
if not IsBound(START_ID) then Error("START_ID must be bound"); fi;
if not IsBound(END_ID) then Error("END_ID must be bound"); fi;
if not IsBound(OUT_PATH) then Error("OUT_PATH must be bound"); fi;
if not IsBound(DIM) then DIM := 8; fi;
if not IsBound(USE_SMALL_GENERATING_SET) then USE_SMALL_GENERATING_SET := false; fi;

Read(Concatenation(SCRIPT_DIR, "/sp8_common.g"));

ctx := SP8_BuildContext(DIM);;
P := ctx.P;;

PrintTo(OUT_PATH, "rep_id\torder\tgenerator_count\tgenerator_orders\tmatrix_hex\n");

for rep_id in [START_ID..END_ID] do
    rep_path := Concatenation(RUN_DIR, "/reps/rep_", String(rep_id), ".g");;
    if IsExistingFile(rep_path) then
        H := SP8_LoadRepFromRun(P, RUN_DIR, rep_id);;
        mats := SP8_PreimageMatrixGenerators(ctx, H, USE_SMALL_GENERATING_SET);;
        hex := SP8_MatrixGeneratorHexString(mats);;
        orders := JoinStringsWithSeparator(List(mats, m -> String(Order(m))), ",");;
        AppendTo(OUT_PATH,
            String(rep_id), "\t",
            String(Order(H)), "\t",
            String(Length(mats)), "\t",
            orders, "\t",
            hex, "\n"
        );
    fi;
od;

QUIT_GAP(0);
