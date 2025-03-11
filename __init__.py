bl_info = {
    "name": "ESP32 Multi-Bone & Object Motion Capture",
    "blender": (3, 0, 0),
    "category": "Animation",
    "author": "Your Name",
    "version": (3, 4),
    "description": "Real-time Multi-Bone & Object Animation via UDP from ESP32 with Manual Mapping",
    "location": "View3D > N-Panel > ESP32 Motion",
}

import bpy
import socket
import threading
import json
import time

# UDP Settings
UDP_IP = "0.0.0.0"
UDP_PORT = 12345
sock = None  
running = False
motion_data = {}
base_frame = None
start_time = None

class BoneMappingProperty(bpy.types.PropertyGroup):
    esp32_bone: bpy.props.StringProperty(name="ESP32 Bone Name")
    blender_bone: bpy.props.StringProperty(name="Blender Bone Name")

class ObjectMappingProperty(bpy.types.PropertyGroup):
    esp32_object: bpy.props.StringProperty(name="ESP32 Object Name")
    blender_object: bpy.props.StringProperty(name="Blender Object Name")

def update_motion():
    global motion_data, base_frame, start_time
    if not motion_data:
        return 0.05  

    current_time = time.time()
    current_frame = base_frame + int((current_time - start_time) / 0.05)
    bpy.context.scene.frame_set(current_frame)

    for obj in bpy.data.objects:
        # Bone-Level Mapping
        if obj.type == 'ARMATURE' and hasattr(obj, "bone_mapping"):
            bpy.ops.object.mode_set(mode='POSE')
            for mapping in obj.bone_mapping:
                if mapping.esp32_bone in motion_data:
                    bone = obj.pose.bones.get(mapping.blender_bone)
                    if bone:
                        roll, pitch, yaw = motion_data[mapping.esp32_bone]
                        bone.rotation_mode = 'XYZ'
                        bone.rotation_euler = (pitch * 0.0174533, roll * 0.0174533, yaw * 0.0174533)
                        bone.keyframe_insert(data_path="rotation_euler", frame=current_frame)

        # Object-Level Mapping
        if hasattr(obj, "object_mapping"):
            for mapping in obj.object_mapping:
                if mapping.esp32_object in motion_data:
                    obj.location.x, obj.location.y, obj.location.z = motion_data[mapping.esp32_object]
                    obj.keyframe_insert(data_path="location", frame=current_frame)

    return 0.05

def udp_listener():
    global running, motion_data, sock
    while running:
        try:
            data, _ = sock.recvfrom(1024)
            json_data = json.loads(data.decode())

            for key, value in json_data.items():
                if isinstance(value, list) and len(value) == 3:
                    motion_data[key] = tuple(value)

        except socket.timeout:
            pass  
        except Exception as e:
            print(f"UDP Error: {e}")

def start_capture():
    global running, base_frame, start_time, sock
    if running:
        return {'CANCELLED'}

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        sock.settimeout(1.0)  

        running = True
        base_frame = bpy.context.scene.frame_current
        start_time = time.time()

        threading.Thread(target=udp_listener, daemon=True).start()
        bpy.app.timers.register(update_motion, first_interval=0.05, persistent=True)

        return {'FINISHED'}

    except Exception as e:
        print(f"Failed to start UDP connection: {e}")
        return {'CANCELLED'}

def stop_capture():
    global running, sock
    if not running:
        return {'CANCELLED'}

    running = False
    bpy.app.timers.unregister(update_motion)

    if sock:
        sock.close()
        sock = None

    return {'FINISHED'}

class ESP32_OT_StartMotion(bpy.types.Operator):
    bl_idname = "esp32.start_motion"
    bl_label = "Start Capture"
    def execute(self, context):
        return start_capture()

class ESP32_OT_StopMotion(bpy.types.Operator):
    bl_idname = "esp32.stop_motion"
    bl_label = "Stop Capture"
    def execute(self, context):
        return stop_capture()

class ESP32_OT_AddBone(bpy.types.Operator):
    bl_idname = "esp32.add_bone"
    bl_label = "Assign ESP32 Bone"
    def execute(self, context):
        obj = bpy.context.object
        if not obj or obj.type != 'ARMATURE':
            return {'CANCELLED'}
        selected_bone = bpy.context.active_pose_bone
        if not selected_bone:
            return {'CANCELLED'}
        mapping = obj.bone_mapping.add()
        mapping.blender_bone = selected_bone.name
        return {'FINISHED'}

class ESP32_OT_RemoveBone(bpy.types.Operator):
    bl_idname = "esp32.remove_bone"
    bl_label = "Remove Assigned Bone"
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        obj = bpy.context.object
        if obj and obj.type == 'ARMATURE' and 0 <= self.index < len(obj.bone_mapping):
            obj.bone_mapping.remove(self.index)
        return {'FINISHED'}

class ESP32_OT_AddObject(bpy.types.Operator):
    bl_idname = "esp32.add_object"
    bl_label = "Assign ESP32 Object"
    def execute(self, context):
        obj = bpy.context.object
        if not obj:
            return {'CANCELLED'}
        mapping = obj.object_mapping.add()
        mapping.blender_object = obj.name
        return {'FINISHED'}

class ESP32_OT_RemoveObject(bpy.types.Operator):
    bl_idname = "esp32.remove_object"
    bl_label = "Remove Assigned Object"
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        obj = bpy.context.object
        if obj and 0 <= self.index < len(obj.object_mapping):
            obj.object_mapping.remove(self.index)
        return {'FINISHED'}

class ESP32_PT_Panel(bpy.types.Panel):
    bl_label = "ESP32 Motion Capture"
    bl_idname = "ESP32_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ESP32 Motion"
    
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        
        layout.operator("esp32.add_bone", text="Assign Bone")
        if obj and hasattr(obj, 'bone_mapping'):
            for i, mapping in enumerate(obj.bone_mapping):
                row = layout.row()
                row.prop(mapping, "esp32_bone", text="ESP32 Bone")
                row.label(text=f"-> {mapping.blender_bone}")
                row.operator("esp32.remove_bone", text="X").index = i

        layout.operator("esp32.add_object", text="Assign Object")
        if obj and hasattr(obj, 'object_mapping'):
            for i, mapping in enumerate(obj.object_mapping):
                row = layout.row()
                row.prop(mapping, "esp32_object", text="ESP32 Object")
                row.label(text=f"-> {mapping.blender_object}")
                row.operator("esp32.remove_object", text="X").index = i

        layout.operator("esp32.start_motion", text="Start Capture")
        layout.operator("esp32.stop_motion", text="Stop Capture")

def register():
    bpy.utils.register_class(BoneMappingProperty)
    bpy.utils.register_class(ObjectMappingProperty)
    bpy.types.Object.bone_mapping = bpy.props.CollectionProperty(type=BoneMappingProperty)
    bpy.types.Object.object_mapping = bpy.props.CollectionProperty(type=ObjectMappingProperty)
    bpy.utils.register_class(ESP32_PT_Panel)
    bpy.utils.register_class(ESP32_OT_AddBone)
    bpy.utils.register_class(ESP32_OT_RemoveBone)
    bpy.utils.register_class(ESP32_OT_AddObject)
    bpy.utils.register_class(ESP32_OT_RemoveObject)
    bpy.utils.register_class(ESP32_OT_StartMotion)
    bpy.utils.register_class(ESP32_OT_StopMotion)

def unregister():
    bpy.utils.unregister_class(ESP32_PT_Panel)

if __name__ == "__main__":
    unregister()
    register()
