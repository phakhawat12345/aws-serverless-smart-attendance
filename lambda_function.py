import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AttendanceLogs')

# กำหนดรหัส PIN ประจำคาบเรียน
ACTIVE_PIN = "4829" 

def lambda_handler(event, context):
    try:
        # รองรับ CORS Preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': ''
            }

        # ดึงข้อมูลที่ส่งมาจากหน้าเว็บ Frontend
        body = json.loads(event.get('body', '{}'))
        course_id = body.get('courseId')
        section = body.get('section')
        student_id = body.get('studentId')
        student_name = body.get('studentName')
        entered_pin = body.get('pin')

        # ตรวจสอบว่ากรอกข้อมูลครบถ้วนไหม
        if not course_id or not section or not student_id or not student_name or not entered_pin:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'กรุณากรอกข้อมูลและรหัส PIN ให้ครบถ้วน'})
            }

        # 1. ตรวจสอบความถูกต้องของรหัส PIN
        if entered_pin != ACTIVE_PIN:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'รหัส PIN หน้าห้องไม่ถูกต้อง! กรุณาตรวจสอบใหม่อีกครั้ง'})
            }

        # 2. บันทึกข้อมูลลง DynamoDB (เพิ่ม CourseId และ Section เข้าไป)
        table.put_item(
            Item={
                'StudentId': student_id,
                'CourseId': course_id,
                'Section': section,
                'StudentName': student_name,
                'Status': 'PRESENT'
            }
        )

        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'เช็กชื่อเข้าเรียนสำเร็จ!'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
