# ui/history_manager.py

from collections import deque
import copy
from ui.qt_compat import QObject, Signal

class HistoryManager(QObject):
    history_changed = Signal()
    
    def __init__(self, max_history=1000):
        super().__init__()
        self.max_history = max_history
        self.undo_stack = deque(maxlen=max_history)
        self.redo_stack = deque(maxlen=max_history)
        self.current_state = None
        self.is_undoing = False
        self.is_redoing = False
        
    def record_state(self, state_type, editor_type, data, description=""):
        if self.is_undoing or self.is_redoing:
            return
            
        state = {
            'type': state_type,
            'editor': editor_type, 
            'data': copy.deepcopy(data),
            'description': description
        }
        
        self.undo_stack.append(state)
        self.redo_stack.clear()
        
        self.history_changed.emit()

    def undo(self):
        if not self.undo_stack:
            return None
            
        self.is_undoing = True
        state = self.undo_stack.pop()
        self.redo_stack.append(state)
        
        self.history_changed.emit()
        self.is_undoing = False
        
        return state

    def redo(self):
        if not self.redo_stack:
            return None
            
        self.is_redoing = True
        state = self.redo_stack.pop()
        self.undo_stack.append(state)
        
        self.history_changed.emit()
        self.is_redoing = False
        
        return state
        
    def can_undo(self):
        return len(self.undo_stack) > 0
        
    def can_redo(self):
        return len(self.redo_stack) > 0
        
    def clear(self):
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.history_changed.emit()
        
    def get_history_info(self):
        return {
            'undo_count': len(self.undo_stack),
            'redo_count': len(self.redo_stack),
            'can_undo': self.can_undo(),
            'can_redo': self.can_redo()
        }
