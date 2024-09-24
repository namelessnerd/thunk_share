import os 

"""
mimics a service disco service like consul.
keys are camel cased with intent. The structure is intended to mimic consul
/customer/aiproviders/aiprovider/config
/customer/services/aiprovider/config_for_service
"""

service_configs = {
    "acmeinc" : {
        "aiProviders" : {
            "openAI" :{
                "api_key": os.getenv("OPENAI_API_KEY")
                },
            "anthropic" : {
                "api_key": os.getenv("ANTHROPIC_API_KEY")
                }
        },
        "creatives" : [
                {"openAI" : {
                    "model" : "gpt-4o-2024-08-06",
                    "temperature": "0.7"
                }},
                {"anthropic" : {
                    "model" : "claude-3-5-sonnet-20240620",
                    "temperature": "0.7"
                }}

        ],
        "prescreener" : [
            {
                "openAI" : {
                    "model" : "gpt-4o-2024-08-06",
                    "temperature": "0.5"
                },
                "anthropic" : {
                    "model" : "claude-3-5-sonnet-20240620",
                    "temperature": "0.5"
                }
            }
        ]
    }
}