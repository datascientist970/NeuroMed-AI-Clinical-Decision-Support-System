from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ClinicalInputSerializer
from .ai.clinic_agent import clinical_graph
import logging
logger = logging.getLogger("clinical")
from rest_framework.permissions import IsAuthenticated


def home(request):
    return render(request, "index.html")

class ClinicalDecisionSupportAPIView(APIView):
    """
    Autonomous Clinical Decision Support (Decision-Support Only)
    """

    def post(self, request):
        serializer = ClinicalInputSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Initialize LangGraph state
        state = {
            "input_data": serializer.validated_data
        }

        try:
            result = clinical_graph.invoke(state)
            return Response(
                result["final_output"],
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Clinical AI failure: {str(e)}", exc_info=True)
            return Response(
                {"error": "Internal processing error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClinicalDecisionSupportAPIView(APIView):
    authentication_classes = []
    permission_classes = []
