from rest_framework import serializers
from django.core.exceptions import ValidationError

from career.models import Career_data, Career_structure, Persons
from django.contrib.auth import authenticate, get_user_model


class CareerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career_data
        fields = ('id',
                  'name',
                  'jdata')


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career_data
        fields = ('id',
                  'name'
                  )


class CardsuccessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career_structure
        fields = ('id',
                  'name',
                  'company',
                  'jdata_org_structure',
                  'jdata_org_successor',
                  'persons_list')


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persons
        # fields = '__all__'
        exclude = ('id', 'img')

class SPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persons
        # fields = '__all__'
        exclude = ('id', 'img')

class LoginSerializer(serializers.Serializer):
    """
    This serializer defines two fields for authentication:
      * username
      * password.
    It will try to authenticate the user with when validated.
    """
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        # This will be used when the DRF browsable API is enabled
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        # Take username and password from request
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Try to authenticate the user using Django auth framework.
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                # If we don't have a regular user, raise a ValidationError
                msg = 'Access denied: wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        # We have a valid user, put it in the serializer's validated_data.
        # It will be used in the view.
        attrs['user'] = user
        return attrs


UserModel = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = '__all__'

    def create(self, clean_data):
        user_obj = UserModel.objects.create_user(email=clean_data['email'], password=clean_data['password'])
        user_obj.username = clean_data['username']
        user_obj.save()
        return user_obj


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    ##
    def check_user(self, clean_data):
        user = authenticate(username=clean_data['email'], password=clean_data['password'])
        if not user:
            raise ValidationError('user not found')
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('email', 'username')
