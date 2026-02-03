from rest_framework import serializers

class ClinicalInputSerializer(serializers.Serializer):
    patient_id = serializers.CharField()
    age = serializers.IntegerField(min_value=0, max_value=120)
    gender = serializers.CharField()
    symptoms = serializers.CharField()

    vitals = serializers.DictField()

    lab_results = serializers.CharField(required=False, allow_blank=True)
    clinical_notes = serializers.CharField(required=False, allow_blank=True)

    def validate_vitals(self, value):
        required_keys = [
            "heart_rate",
            "blood_pressure",
            "temperature",
            "oxygen_saturation"
        ]
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"{key} is required in vitals")
        return value
