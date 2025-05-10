from fit_tool.fit_file import FitFile
from fit_tool.fit_file_builder import FitFileBuilder

if __name__ == "__main__":
    # Read the FIT file
    fit_file = FitFile.from_file("current_fit/Locations.fit")

    # Create a new FitFileBuilder
    builder = FitFileBuilder(auto_define=False)

    # Iterate through the records in the original FIT file
    for record in fit_file.records:
        print(record)
    #     include_record = True

    #     if message.global_id == RecordMessage.ID:
    #         # Remove the heart rate field from all record definition and data messages
    #         message.remove_field(RecordHeartRateField.ID)

    #         if isinstance(message, RecordMessage):
    #             # Remove records where the power is too high
    #             power_field = message.get_field(RecordPowerField.ID)
    #             if power_field and power_field.is_valid():
    #                 power = power_field.get_value()
    #                 if power > 800:
    #                     include_record = False

    #     if include_record:
    #         builder.add(message)

    # # Build the modified FIT file
    # modified_file = builder.build()

    # # Save the modified FIT file to a new file
    # modified_file.to_file("../tests/out/modified_activity.fit")

    # # Read the modified FIT file to verify changes
    # fit_file2 = FitFile.from_file("../tests/out/modified_activity.fit")
