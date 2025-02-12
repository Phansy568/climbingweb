from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from agent_client import AgentClient
import logging
import traceback

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 初始化智能体客户端
try:
    agent_client = AgentClient(
        api_key="sk-cfae5cd572eb4452a28e7904ef28e080",
        app_id="acc6de31ffe64442afd8aa028fec870e"
    )
except Exception as e:
    logger.error(f"初始化智能体客户端失败: {str(e)}")
    raise

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/chat/api', methods=['GET', 'POST'])
def chat_api():
    if request.method == 'GET':
        try:
            # 测试智能体连接
            test_result = agent_client.chat(prompt="测试连接")
            if test_result.get('success'):
                return jsonify({
                    'status': 'ok',
                    'message': 'API is running and agent is connected'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'Agent connection failed: {test_result.get("message")}'
                }), 500
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'API test failed: {str(e)}'
            }), 500

    try:
        logger.debug(f"收到请求头: {dict(request.headers)}")
        logger.debug(f"收到请求体: {request.get_data(as_text=True)}")
        
        data = request.json
        if not data:
            raise ValueError("请求体为空")
            
        prompt = data.get('prompt')
        session_id = data.get('session_id')
        message_history = data.get('message_history', [])

        logger.info(f"处理聊天请求 - prompt: {prompt}, session_id: {session_id}")
        logger.debug(f"消息历史: {message_history}")

        if not prompt:
            return jsonify({
                'success': False,
                'message': '请输入消息内容'
            }), 400

        # 调用智能体
        result = agent_client.chat(
            prompt=prompt,
            session_id=session_id
        )
        
        logger.debug(f"智能体响应: {result}")
        
        if not isinstance(result, dict):
            raise ValueError(f"智能体返回了意外的响应格式: {type(result)}")
            
        if result.get('success') and 'session_id' not in result.get('data', {}):
            logger.warning("响应中缺少session_id")
            
        return jsonify(result)

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"处理请求时发生错误: {str(e)}\n{error_details}")
        return jsonify({
            'success': False,
            'message': str(e),
            'details': error_details
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 