import boto3
import json
import numpy as np
import pandas as pd

from botocore.exceptions import ClientError
from helpers import conversation_helper


def invoke_llm(prompt, conversation_id, temperature=0.1, top_p=0.9):
    """
    Invokes Anthropic Claude 3 Sonnet to run an inference using the input
    provided in the request body.

    :param prompt: The prompt that you want Claude 3 to complete.
    :return: Inference response from the model.
    """
    
    # Initialize the Amazon Bedrock runtime client
    client = boto3.client(
        service_name="bedrock-runtime", region_name="us-east-1"
    )
    conversation_helper.check_conversation(conversation_id)
    # Invoke Claude 3 with the text prompt
    model_id = "anthropic.claude-v2:1"

    try:
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "temperature": temperature,
                    "top_p": top_p,
                    "messages": conversation_helper.get_conversation(conversation_id) + [
                        {"role": "user", "content": prompt}
                    ]
                }
            ),
        )

        # Process and print the response
        result = json.loads(response.get("body").read())
        input_tokens = result["usage"]["input_tokens"]
        output_tokens = result["usage"]["output_tokens"]
        output_list = result.get("content", [])
        conversation_helper.add_user_message(conversation_id, prompt)
        conversation_helper.add_assistant_message(conversation_id, output_list)
        
    
        return output_list, conversation_helper.get_conversation(conversation_id)

    except ClientError as err:
        print(
            "Couldn't invoke Claude 3 Sonnet. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise err


def send_prompt(prompt: str, conversation_id: int):
    response, conv = invoke_llm(prompt, conversation_id)
    return (response[0]["text"], conv)
