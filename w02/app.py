from flask import Flask, jsonify
import hiwonder.ActionGroupControl as AGC

# 初始化Flask应用
app = Flask(__name__)

# 创建一个API端点来执行动作
@app.route('/run_action/<string:action_name>', methods=['GET'])
def run_robot_action(action_name):
    try:
        print(f"接收到指令，执行动作: {action_name}")
        # AGC.runAction(action_name)
        return jsonify({"status": "success", "action": action_name})
    except Exception as e:
        print(f"执行动作失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    # 监听所有网络接口，这样局域网内的设备才能访问
    app.run(host='0.0.0.0', port=5000)
