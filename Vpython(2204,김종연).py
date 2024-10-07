import numpy as np
import random as rd
import time
from vpython import *


# 파라미터 설정
infection_rate = 0.3
infection_range = 1.5
recovery_time = 5
mask_effectiveness = 0.8
mortality_rate = 0.05
mask_usage_duration = 100
immune_duration = 4

class Person:
    def __init__(self, is_ai=False):
        self.health = 100
        self.food = 100
        self.depression = 20
        self.is_infected = False
        self.is_immune = False
        self.is_ai = is_ai
        self.infection_time = None
        self.mask_on = False
        self.mask_timer = 0
        self.position = vector(rd.uniform(-10, 10), rd.uniform(-10, 10), 0)
        self.life = True
        self.immune_time = None
        
    
    def update(self, current_time):
        if self.life == False:
            return
        if self.is_infected:
            self.health -= 0.5
            if (int(current_time) - int(self.infection_time) < int(recovery_time+2)) and (int(current_time) - int(self.infection_time) > int(recovery_time-2)):
                # 생존: 면역 상태가 되거나, 일반 상태로 복귀
                if rd.random() < 1:  # 30% 확률로 면역 상태로 전환
                    self.is_immune = True
                    self.health = 100
                    self.recovered_time = current_time  # 면역 시작 시간 기록
                    self.shape.color = vector(0, 0, 1)  # 파란색 (면역 상태)
                    self.is_infected = False
                    self.immune_time = current_time

                elif rd. random() < 0.3:
                    # 생존했으나 일반 상태로 복귀
                    self.health = 100
                    self.shape.color = vector(0, 1, 0)  # 초록색 (일반 상태)
                    self.is_infected = False

        if self.food <= 30:
            self.health -= 0.05

        if self.depression > 95:
            self.health -= 100


        if self.health < 0:
            self.life = False
            # self.shape.color = vector(0,0,0)


        if self.is_immune == True:
            if (int(current_time) - int(self.immune_time) < int(immune_duration+2)) and (int(current_time) - int(self.immune_time) > int(immune_duration-2)):
                self.immune = False


        if self.mask_on:
            self.mask_timer += 1
            if self.mask_timer >= mask_usage_duration: 
                self.mask_on = False
                # self.shape.color = vector(0, 1, 0)  # 마스크 벗으면 다시 초록색 


        
    def infect(self, current_time):
        if self.life == False:
            return
        if self.is_immune == True:
            return
        self.is_infected = True
        self.infection_time = current_time
        self.shape.color = vector(1, 1, 0)  # 노란색 (감염됨)



            


# 강화학습 에이전트 (Q-learning)
class QLearningAgent:
    def __init__(self, actions):
        self.q_table = {}  # Q 테이블 초기화
        self.actions = actions
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1

    def get_q_value(self, state, action):
        if (state, action) not in self.q_table:
            self.q_table[(state, action)] = 0.0
        return self.q_table[(state, action)]

    def choose_action(self, state):
        if np.random.rand() < self.epsilon:
            return rd.choice(self.actions)
        else:
            q_values = [self.get_q_value(state, action) for action in self.actions]
            max_q_value = max(q_values)
            return self.actions[q_values.index(max_q_value)]

    def update_q_value(self, state, action, reward, next_state):
        max_next_q_value = max([self.get_q_value(next_state, a) for a in self.actions])
        self.q_table[(state, action)] = self.get_q_value(state, action) + \
                                        self.learning_rate * (reward + self.discount_factor * max_next_q_value - self.get_q_value(state, action))





# 시뮬레이션 초기화
population = []
actions = ["출근", "마스크 착용", "재택 근무", "여가 활동"]
agent = QLearningAgent(actions)

for i in range(49):
    person = Person(is_ai=False)
    population.append(person)

# AI 객체 생성
ai_person = Person(is_ai=True)
population.append(ai_person)

# 상태를 정의하는 함수
def get_state(person):
    return (person.health, person.food, person.is_infected, person.depression)

# 보상 시스템
def calculate_reward(person):
    if person.health <= 0:
        return -100  # 사망하면 큰 패널티
    elif person.is_infected:
        return -100  # 감염되면 패널티
    else:
        return 30  # 감염되지 않고 생존하면 보상

# 학습 루프
for episode in range(1000):  # 여러 번의 시뮬레이션

    current_time = time.time()
    # 상태 초기화
    state = get_state(ai_person)
    
    for _ in range(100):  # 각 에피소드에서 100번의 행동
        # 현재 상태에서 행동 선택
        action = agent.choose_action(state)
        
        # 선택한 행동에 따라 상태 업데이트
        if action == "출근":
            ai_person.food += 5
            ai_person.depression -= 3
            ai_person.position += vector(rd.uniform(-1, 1), rd.uniform(-1, 1), 0)
        elif action == "마스크 착용":
            ai_person.mask_on = True
            ai_person.health -= 2     
        elif action == "재택 근무":
            ai_person.food -= 5
            ai_person.depression += 10
        elif action == "여가 활동":
            ai_person.depression -= 15
            ai_person.position += vector(rd.uniform(-2,2), rd.uniform(-2, 2), 0)
            ai_person.mask_on = False


        # 화면 밖으로 나가지 않도록 이동 제한
        if ai_person.position.x > 20:
            ai_person.position.x = 20
        elif ai_person.position.x < -20:
            ai_person.position.x = -20
        if ai_person.position.y > 15:
            ai_person.position.y = 15
        elif ai_person.position.y < -15:
            ai_person.position.y = -15

        for i in range(0,49):
            visual_person = population[i]
            visual_person.position.x += rd.uniform(-0.5, 0.5)
            visual_person.position.y += rd.uniform(-0.5, 0.5)
            visual_person.update(current_time)

        # 상태 업데이트
        ai_person.update(current_time)
        
        # 보상 계산
        reward = calculate_reward(ai_person)
        
        # 다음 상태 가져오기
        next_state = get_state(ai_person)
        
        # Q 테이블 업데이트
        agent.update_q_value(state, action, reward, next_state)
        
        # 상태 갱신
        state = next_state


# 강화학습 종료 후 Q-테이블 출력
for state_action, q_value in agent.q_table.items():
    state, action = state_action
    print(f"State: {state}, Action: {action}, Q-value: {q_value}")




# 사용자 정의 변수: 초기 감염된 사람 수
initial_infected_count = 3  # 설정 가능한 초기 감염자 수 (AI 객체 제외)



# 사람 클래스 수정 (VPython을 사용하여 사람들을 화면에 표시하기 위한 객체)
class Visual_Person:
    def __init__(self, is_ai=False):
        self.health = 100
        self.food = 100
        self.depression = 20
        self.is_infected = False
        self.is_immune = False
        self.is_ai = is_ai
        self.infection_time = None
        self.mask_on = False
        self.mask_timer = 0
        self.position = vector(rd.uniform(-10, 10), rd.uniform(-10, 10), 0)
        self.life = True
        self.immune_time = None
        self.i = 0

        if is_ai:
            self.shape = box(pos=self.position, length=1, height=1, width=0.5, color=vector(1, 0, 0))  # 빨간색 (AI)
        else:
            self.shape = sphere(pos=self.position, radius=0.5, color=vector(0, 1, 0))  # 초록색 (일반 사람)
        
    
    def update(self, current_time,i,is_ai=False):
        if self.life == False:
            return
        if self.is_infected:
            self.health -= 0.5
            if (int(current_time) - int(self.infection_time) < int(recovery_time+2)) and (int(current_time) - int(self.infection_time) > int(recovery_time-2)):
                # 생존: 면역 상태가 되거나, 일반 상태로 복귀
                if rd.random() < 0.2:  # 30% 확률로 면역 상태로 전환
                    self.is_immune = True
                    self.health = 100
                    self.recovered_time = current_time  # 면역 시작 시간 기록
                    self.shape.color = vector(0, 0, 1)  # 파란색 (면역 상태)
                    self.is_infected = False
                    self.immune_time = current_time

                elif rd. random() < 0.2:
                    # 생존했으나 일반 상태로 복귀
                    self.health = 100
                    self.shape.color = vector(0, 1, 0)  # 초록색 (일반 상태)
                    self.is_infected = False

        if self.depression > 95:
            self.health -= 100

        if self.food <= 30:
            self.health -= 0.05

        if self.health < 0:
            self.life = False
            self.shape.color = vector(0,0,0)

        if self.position.x > 20:
            self.position.x = 20
        elif self.position.x < -20:
            self.position.x = -20
        if self.position.y > 15:
            self.position.y = 15
        elif self.position.y < -15:
            self.position.y = -15

        self.shape.pos = self.position

        if self.is_immune == True:
            if (int(current_time) - int(self.immune_time) < int(immune_duration+2)) and (int(current_time) - int(self.immune_time) > int(immune_duration-2)):
                self.immune = False
                self.shape.color = vector(0, 1, 0)

        if self.mask_on:
            self.mask_timer += 1
            if self.mask_timer >= mask_usage_duration: 
                self.mask_on = False
                self.shape.color = vector(0, 1, 0)  # 마스크 벗으면 다시 초록색 


        
    def infect(self, current_time):
        if self.life == False:
            return
        if self.is_immune == True:
            return
        self.is_infected = True
        self.infection_time = current_time
        self.shape.color = vector(1, 1, 0)  # 노란색 (감염됨)


# 새로운 시뮬레이션 환경 설정
visual_population = []

# 기존 population을 기반으로 VPython 객체를 생성
for i in range(49):
    visual_person = Visual_Person(is_ai=False)
    visual_population.append(visual_person)


# AI 객체 생성
visual_ai_person = Visual_Person(is_ai=True)
visual_population.append(visual_ai_person)


# 초기 감염자 설정
def initialize_infected_population(infected_count):
    current_time = time.time()
    infected_people = rd.sample(visual_population, infected_count)  # 무작위로 감염될 사람 선택
    for person in infected_people:
        person.infect(current_time)  # 선택된 사람 감염 처리


# 감염자 수 설정 (사용자가 설정한 값에 따라)
initialize_infected_population(initial_infected_count)

result = [0,0,0,0]
# 시뮬레이션 루프 실행
def run_simulation(visual_population):
    
    visual_ai_person = visual_population[49]

    # if visual_ai_person.life == False:
    #     return
    for _ in range(2000):  # 300 프레임 동안 실행
        current_time = time.time()
        rate(30)  # 시뮬레이션 속도 (초당 30 프레임)

        # AI 객체의 상태 가져오기
        state = get_state(visual_ai_person)

        # 학습된 모델을 사용하여 행동 선택
        action = agent.choose_action(state)

        # 행동에 따른 업데이트
        if action == "출근":
            visual_ai_person.food += 5
            visual_ai_person.depression -= 3
            visual_ai_person.position += vector(rd.uniform(-1, 1), rd.uniform(-1, 1), 0)

            visual_ai_person.mask_on = False
            result[0] +=1 
        elif action == "마스크 착용":
            visual_ai_person.mask_on = True
            visual_ai_person.shape.color = vector(0.5, 0.5, 0.5)  # 마스크 착용 시 회색
            result[1] +=1
        elif action == "재택 근무":
            visual_ai_person.food -= 5
            visual_ai_person.depression += 10
            result[2]+=1
        elif action == "여가 활동":
            visual_ai_person.depression -= 15
            visual_ai_person.position += vector(rd.uniform(-2, 2), rd.uniform(-2, 2), 0)
            visual_ai_person.mask_on = False
            result[3] +=1


        if visual_ai_person.position.x > 20:
            visual_ai_person.position.x = 20
        elif visual_ai_person.position.x < -20:
            visual_ai_person.position.x = -20
        if visual_ai_person.position.y > 15:
            visual_ai_person.position.y = 15
        elif visual_ai_person.position.y < -15:
            visual_ai_person.position.y = -15

            
        # AI 상태 업데이트
        visual_ai_person.update(current_time,49)

        # 나머지 애들 상태 업데이트
        for i in range(0,49):
            visual_person = visual_population[i]
            visual_person.position.x += rd.uniform(-0.5, 0.5)
            visual_person.position.y += rd.uniform(-0.5, 0.5)
            visual_person.update(current_time,i)

        # 감염 확산 로직 (기존 시뮬레이션과 동일하게 설정)
        spread_infection(visual_population + [visual_ai_person], current_time)




# 감염 전파 함수 정의
def spread_infection(population, current_time):
    for person in population:
        if person.is_infected:  # 감염된 사람만 전파 가능
            for other in population:
                if other != person and not other.is_immune and not other.is_infected:
                    distance = mag(person.position - other.position)
                    if distance < infection_range:  # 감염 범위 내에 있을 때
                        infection_chance = infection_rate
                        if other.mask_on:
                            infection_chance *= (1 - mask_effectiveness)  # 마스크 착용 시 감염률 감소
                        if rd.random() < infection_chance:
                            other.infect(current_time=current_time)

# 시뮬레이션 실행
run_simulation(visual_population)

print(result) 