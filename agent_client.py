import os
from http import HTTPStatus
from typing import Optional, Dict, List
from dashscope import Application
import logging

logger = logging.getLogger(__name__)

class AgentClient:
    def __init__(self, api_key: str, app_id: str):
        self.api_key = api_key
        self.app_id = app_id
        logger.info(f"初始化AgentClient - app_id: {app_id}")
        
    def chat(self, 
             prompt: str,
             session_id: Optional[str] = None,
             stream: bool = False,
             has_thoughts: bool = False,
             memory_id: Optional[str] = None,
             image_list: Optional[List[str]] = None,
             biz_params: Optional[Dict] = None) -> Dict:
        """
        调用百炼智能体进行对话
        
        Args:
            prompt: 输入提示词
            session_id: 会话ID,用于多轮对话
            stream: 是否使用流式输出
            has_thoughts: 是否输出思考过程
            memory_id: 长期记忆ID
            image_list: 图片URL列表
            biz_params: 业务参数
            
        Returns:
            Dict: 智能体响应结果
        """
        try:
            logger.debug(f"准备调用智能体 - prompt: {prompt}, session_id: {session_id}")
            
            # 验证 API key
            if not self.api_key or not self.app_id:
                raise ValueError("API key 或 app_id 未设置")
            
            params = {
                "api_key": self.api_key,
                "app_id": self.app_id,
                "prompt": prompt
            }
            
            # 确保session_id被正确传递
            if session_id:
                logger.debug(f"使用现有session_id: {session_id}")
                params["session_id"] = session_id
            if has_thoughts:
                params["parameters"] = {"has_thoughts": True}
            if memory_id:
                params["memory_id"] = memory_id
            if image_list:
                params["image_list"] = image_list
            if biz_params:
                params["biz_params"] = biz_params
                
            logger.debug(f"调用参数: {params}")
            
            try:
                # 调用智能体
                if stream:
                    response = Application.streamCall(**params)
                else:
                    response = Application.call(**params)
                
                logger.debug(f"智能体原始响应: {response}")
                
                # 处理响应
                if response.status_code != HTTPStatus.OK:
                    error_msg = f"智能体调用失败 - code: {response.status_code}, message: {response.message}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "request_id": response.request_id,
                        "code": response.status_code,
                        "message": response.message
                    }
                
                # 确保返回session_id
                return {
                    "success": True,
                    "data": {
                        "text": response.output.text.replace('\n', '  \n'),
                        "session_id": response.output.session_id if hasattr(response.output, 'session_id') else None
                    },
                    "usage": response.usage
                }
                
            except Exception as e:
                logger.error(f"调用智能体API时发生错误: {str(e)}", exc_info=True)
                return {
                    "success": False,
                    "message": f"API调用失败: {str(e)}"
                }
            
        except Exception as e:
            logger.error(f"调用智能体时发生错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": str(e)
            }

# 使用示例
if __name__ == "__main__":
    client = AgentClient(
        api_key="sk-cfae5cd572eb4452a28e7904ef28e080",
        app_id="acc6de31ffe64442afd8aa028fec870e"
    )
    
    # 简单对话调用
    result = client.chat(prompt="你是谁？")
    if result["success"]:
        print(result["data"].text)
    else:
        print(f"错误: {result['message']}") 