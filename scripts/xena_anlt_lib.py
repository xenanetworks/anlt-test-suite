import asyncio
from xoa_driver import testers, modules, ports, enums
from xoa_driver.hlfuncs import mgmt, anlt
import logging
from contextlib import suppress

#region high-level functions

async def change_module_media(
    tester: testers.L23Tester,
    module: modules.Z800FreyaModule,
    username: str,
    module_media: enums.MediaConfigurationType,
    port_count: int,
    port_speed: int,
    logger: logging.Logger,
    ):
    """Change test module media configuration
    """

    # To do the module reconfiguration
    logger.info(f"#########################################")
    logger.info(f"Chassis:        {tester.info.host}")
    logger.info(f"Username:       {username}")
    logger.info(f"Module:         {module.module_id}")
    logger.info(f"#########################################")

    logger.info(f"Configuring module {module.module_id} to:")
    logger.info(f"    Media configuration: {module_media.name}")
    logger.info(f"    Port configuration: {port_count}x{port_speed}G")

    # the module must be a freya module
    if not isinstance(module, modules.Z800FreyaModule):
        logger.warning(f"The module is not a Freya module")
        logger.warning(f"Abort")
        return None

    # module reservation
    logger.info(f"Reserve module")
    await mgmt.free_tester(tester=tester)
    await mgmt.free_module(module, should_free_ports=True)
    await mgmt.reserve_module(module)
    logger.info(f"----")

    # change module media
    logger.info(f"Change module media to {module_media.name}")
    await module.media.set(media_config=module_media)
    logger.info(f"----")

    # Change module's port config
    speeds = [port_count]
    speeds.extend([port_speed * 1000] * port_count)
    logger.info(f"Change module port config to {speeds}")
    await module.cfp.config.set(portspeed_list=speeds)
    logger.info(f"----")

    await mgmt.free_module(module, should_free_ports=True)
    logger.info(f"Module media change done")


async def verify_frame_lock_both_sides(
    port: ports.Z800FreyaPort,
    serdes: int,
    logger: logging.Logger,
    timeout: int = 20,
    ):
    """Verify that both the exerciser and the DUT port are able to detect frame lock
    """
    # get the connection, module index, and port index from the port object
    # conn, mid, pid = anlt.get_ctx(port)
    logger.info(f"Verifying LT Frame Lock on both ends")

    # set flag to default
    _local = enums.LinkTrainFrameLock.LOST
    _remote = enums.LinkTrainFrameLock.LOST

    # start timeout loops
    for _ in range(timeout):
        # read LT frame lock status of both local and remote
        lt_info = await port.l1.serdes[serdes].lt_info.get()
        # lt_info = await commands.PL1_LINKTRAININFO(conn, mid, pid, serdes, 0).get()
        _local = lt_info.frame_lock
        _remote = lt_info.remote_frame_lock

        # if locked on both sides, return true
        if (
            _local == enums.LinkTrainFrameLock.LOCKED
            and _remote == enums.LinkTrainFrameLock.LOCKED
        ):
            logger.info(f"Frame Lock detected on both ends")
            return True
        # if not, wait 0.1 sec and try again
        else:
            await asyncio.sleep(0.1)

    # if still false after timeout loops, report the error and return false
    logger.warning(f"Frame Lock NOT detected on either end")
    logger.warning(f"Local: {enums.LinkTrainFrameLock(_local).name}. Remote: {enums.LinkTrainFrameLock(_remote).name}")
    raise Exception(f"Local frame lock: {enums.LinkTrainFrameLock(_local).name}. Remote frame lock: {enums.LinkTrainFrameLock(_remote).name}")


async def verify_an_good_check(
    port: ports.Z800FreyaPort,
    logger: logging.Logger,
    timeout: int = 10,
    ) -> bool:
    """Check if Auto-Negotiation status is AN_GOOD_CHECK
    """
    # get the connection, module index, and port index from the port object
    # conn, mid, pid = anlt.get_ctx(port)
    logger.info(f"Verifying AN status on Xena port (must be AN_GOOD_CHECK)")

    # start timeout loops
    for _ in range(timeout):
        # read AN status
        resp = await port.l1.anlt.an.status.get()
        # resp = await commands.PL1_AUTONEG_STATUS(conn, mid, pid).get()
        
        # if AN status is AN_GOOD_CHECK, return true
        if resp.autoneg_state == enums.AutoNegStatus.AN_GOOD_CHECK:
            logger.info(f"AN_GOOD_CHECK detected on Xena port")
            return True
        # if not, wait 0.1 sec and try again
        else:
            await asyncio.sleep(0.1)
    logger.warning(f"AN_GOOD_CHECK not detected on Xena port")
    return False


async def start_anlt_on_dut(
    chassis_ip: str,
    module_id: int,
    port_id: int,
    username: str,
    should_link_recovery: bool,
    should_an: bool,
    logger: logging.Logger,
    should_lt: bool = True,
    ):
    """Start ANLT on a Freya port that emulates a DUT port
    """

    async with testers.L23Tester(chassis_ip, username) as tester:
        logger.info(f"#########################################")
        logger.info(f"Chassis:        {chassis_ip}")
        logger.info(f"Username:       {username}")
        logger.info(f"DUT port:       {module_id}/{port_id}")
        logger.info(f"#########################################")

        # access module on the tester
        module = tester.modules.obtain(module_id)

        # the module must be a freya module
        if not isinstance(module, modules.Z800FreyaModule):
            logger.warning(f"The module is not a Freya module")
            logger.warning(f"Abort")
            return None

        resp = await module.media.get()
        media_str = enums.MediaConfigurationType(resp.media_config).name

        # access port on the module and logger.info out the actual media config
        port = module.ports.obtain(port_id)
        p_count = len(module.ports)
        resp = await port.speed.current.get()
        p_speed = resp.port_speed

        # get serdes count on the port
        resp = await port.capabilities.get()
        serdes_cnt = resp.serdes_count

        # show port media type etc
        logger.info(f"Port {module_id}/{port_id} media type:")
        logger.info(f"  Media: {media_str}")
        logger.info(f"  Speed: {p_count}x{int(p_speed/1000)}G")
        logger.info(f"  Serdes count: {serdes_cnt}")
        logger.info(f"Total port count: {p_count}")
        logger.info(f"----")

        # reserve the port and reset the port
        await mgmt.free_module(module, should_free_ports=True)
        await mgmt.reserve_port(port)
        await mgmt.reset_port(port)

        # autotune taps
        for i in range(serdes_cnt):
            logger.info(f"Reset DUT port {port.kind.module_id}/{port.kind.port_id} Tx taps on serdes lane {i}")
            await port.serdes[i].phy.autotune.set_off()
            await port.serdes[i].phy.autotune.set_on()
        logger.info(f"Waiting for 5 seconds")
        await asyncio.sleep(5)

        # config link recovery (anlt recovery --off)
        await anlt.anlt_link_recovery(port=port, restart_link_down=should_link_recovery, restart_lt_failure=should_link_recovery)

        # put the port into AN = ON, LT = INTERACTIVE, LT preset0 = standard,
        logger.info(f"Setting port {module_id}/{port_id} into:")
        logger.info(f"  AN          = {'On' if should_an else 'Off'} (not allow loopback)")
        logger.info(f"  LT          = On (interactive)")
        logger.info(f"  LT Preset 0 = standard")
        await anlt.anlt_start(
            port=port,
            should_do_an=should_an,
            should_do_lt=should_lt,
            should_lt_interactive=False,
            an_allow_loopback=False,
            lt_preset0=enums.FreyaOutOfSyncPreset.IEEE,
            lt_initial_modulations={},
            lt_algorithm={},
            should_enable_lt_timeout=False
        )
        logger.info(f"----")


async def stop_anlt_on_dut(
    chassis_ip: str,
    module_id: int,
    port_id: int,
    username: str,
    logger: logging.Logger,
    ):
    """Stop ANLT on a Freya port that emulates a DUT port
    """

    # connect to tester using context manager
    async with testers.L23Tester(chassis_ip, username) as tester:
        logger.info(f"#########################################")
        logger.info(f"Chassis:        {chassis_ip}")
        logger.info(f"Username:       {username}")
        logger.info(f"Test port:      {module_id}/{port_id}")
        logger.info(f"#########################################")

        # access module on the tester
        module = tester.modules.obtain(module_id)

        # the module must be a freya module
        if not isinstance(module, modules.Z800FreyaModule):
            logger.warning(f"The module is not a Freya module")
            logger.warning(f"Abort")
            return None

        # resp = await module.media.get()
        # media_str = enums.MediaConfigurationType(resp.media_config).name

        # access port on the module and logger.info out the actual media config
        port = module.ports.obtain(port_id)
        # p_count = len(module.ports)
        # resp = await port.speed.current.get()
        # p_speed = resp.port_speed

        # get serdes count on the port
        # resp = await port.capabilities.get()
        # serdes_cnt = resp.serdes_count

        # reserve the port and reset the port
        await mgmt.free_module(module, should_free_ports=True)
        await mgmt.reserve_port(port)
        await mgmt.reset_port(port)

        logger.info(f"Stopping ANLT on DUT Port {port.kind.module_id}/{port.kind.port_id}")
        await anlt.anlt_stop(port)

        # free the port
        await mgmt.free_port(port)
        
        logger.info(f"----")


async def abort_test(
        port: ports.Z800FreyaPort,
        logger: logging.Logger, 
        ):
    """Stop ANLT on a port and release the port
    """
    logger.info(f"Stopping ANLT on Xena Port {port.kind.module_id}/{port.kind.port_id}")
    await anlt.anlt_stop(port)
    logger.info(f"Test aborted")

    # free the port
    await mgmt.free_port(port)


async def connect_reserver_reset(
    chassis_ip: str,
    module_id: int,
    port_id: int,
    username: str,
    logger: logging.Logger
    ):
    """Connect to Xena chassis and reserve a Freya port
    """

    # connect to Xena tester
    tester = await testers.L23Tester(chassis_ip, username)

    logger.info(f"#########################################")
    logger.info(f"Chassis:        {chassis_ip}")
    logger.info(f"Username:       {username}")
    logger.info(f"Test port:      {module_id}/{port_id}")
    logger.info(f"#########################################")

    # access module on the tester
    module = tester.modules.obtain(module_id)

    # the module must be a freya module
    if not isinstance(module, modules.Z800FreyaModule):
        return None

    # resp = await module.media.get()
    # media_str = enums.MediaConfigurationType(resp.media_config).name

    # access port on the module and # logger.info out the actual media config
    port = module.ports.obtain(port_id)
    # p_count = len(module.ports)
    # resp = await port.speed.current.get()
    # p_speed = resp.port_speed

    # get serdes count on the port
    # resp = await port.capabilities.get()
    # serdes_cnt = resp.serdes_count

    # reserve the port and reset the port
    await mgmt.free_module(module, should_free_ports=True)
    await mgmt.reserve_port(port)
    await mgmt.reset_port(port)
    return port


async def reset_freya_port_tx_tap(
    port: ports.Z800FreyaPort,
    logger: logging.Logger,
    ):
    """Reset Xena port Tx tap values
    """
    # get serdes count on the port
    resp = await port.capabilities.get()
    serdes_cnt = resp.serdes_count
    # reset each serdes's tx taps
    for i in range(serdes_cnt):
        logger.info(f"Reset Xena port {port.kind.module_id}/{port.kind.port_id} Tx taps on serdes lane {i}")
        await port.serdes[i].phy.autotune.set_off()
        await port.serdes[i].phy.autotune.set_on()
    
    logger.info(f"Waiting for 5 seconds")
    await asyncio.sleep(5)


async def reset_dut_port_tx_tap(
    port: ports.Z800FreyaPort,
    serdes_idx: int,
    logger: logging.Logger,
    ):
    """Reset DUT port Tx tap values
    """
    # reset tx taps of the specified serdes
    logger.info(f"Reset DUT port {port.kind.module_id}/{port.kind.port_id} Tx taps on serdes lane {serdes_idx}")
    await port.serdes[serdes_idx].phy.autotune.set_off()
    await port.serdes[serdes_idx].phy.autotune.set_on()
    logger.info(f"Waiting for 5 seconds")
    await asyncio.sleep(5)

#endregion

#region anlt test functions

async def pam4_preset_framelock(
    logger: logging.Logger,
    port: ports.Z800FreyaPort,
    should_link_recovery: bool,
    should_an: bool,
    preset: int,
    serdes: int,
    an_good_check_retries: int,
    frame_lock_retries: int,
    should_pam4pre: bool,
)-> bool:
    
    """Common ANLT prep procedure
    """
    # config link recovery (anlt recovery --off)
    await anlt.anlt_link_recovery(port=port, restart_link_down=should_link_recovery, restart_lt_failure=should_link_recovery)

    # set Xena port LT = INTERACTIVE, LT preset0 = IEEE, timeout = disabled
    # this is because we want the test script to control the LT procedure, not the port automatically does the LT algorithm
    logger.info(f"Setting port into:")
    logger.info(f"  AN          = {'On' if should_an else 'Off'} (not allow loopback)")
    logger.info(f"  LT          = On (interactive)")
    logger.info(f"  LT Preset 0 = current")
    await anlt.anlt_start(
        port=port,
        should_do_an=should_an,
        should_do_lt=True,
        should_lt_interactive=True,
        an_allow_loopback=False,
        lt_preset0=enums.FreyaOutOfSyncPreset.CURRENT,
        lt_initial_modulations={},
        lt_algorithm={},
        should_enable_lt_timeout=False
    )
    logger.info(f"----")

    # 1. if AN is on, make sure AN_GOOD_CHECK is detected before progressing
    if should_an:
        if not await verify_an_good_check(port=port, timeout=an_good_check_retries, logger=logger):
            await abort_test(port, logger)
            return False

    # 2. verify that both ends see Frame Lock
    try:
        await verify_frame_lock_both_sides(port=port, serdes=serdes, logger=logger, timeout=frame_lock_retries)
    except:
        await abort_test(port, logger)
        return False

    # 3. ask the remote port to switch to PAM4 or PAM4Pre
    if not should_pam4pre:
        logger.info(f"Requesting the remote port to switch to PAM4")
        resp = await anlt.lt_encoding(
            port=port, serdes=serdes, encoding=enums.LinkTrainEncoding.PAM4
        )
        if resp != enums.LinkTrainCmdResults.SUCCESS:
            await abort_test(port, logger)
            return False
    else:
        logger.info(f"Requesting the remote port to switch to PAM4 Precoding")
        resp = await anlt.lt_encoding(
            port=port, serdes=serdes, encoding=enums.LinkTrainEncoding.PAM4_WITH_PRECODING
        )
        if resp != enums.LinkTrainCmdResults.SUCCESS:
            await abort_test(port, logger)
            return False
    
    # 4. ask the remote port to use a preset
    logger.info(f"Requesting the remote port to use Preset {preset}")
    resp = await anlt.lt_preset(
        port=port, serdes=serdes, preset=enums.LinkTrainPresets(preset-1)
    )
    if resp != enums.LinkTrainCmdResults.SUCCESS:
        await abort_test(port, logger)
        return False

    return True


async def preset_frame_lock(
    logger: logging.Logger,
    chassis_ip: str,
    module_id: int,
    port_id: int,
    username: str,
    should_link_recovery: bool,
    should_an: bool,
    preset: int,
    serdes: int,
    an_good_check_retries: int,
    frame_lock_retries: int,
    should_pam4pre: bool
) -> bool:
    
    # connect to chassis, reserve and reset the Xena port
    port = await connect_reserver_reset(chassis_ip, module_id, port_id, username, logger)
    if not isinstance(port, ports.Z800FreyaPort):
        logger.info(f"Non-Freya port is used. Aborted")
        return False
    
    # reset Xena port TX taps to have a clean start
    await reset_freya_port_tx_tap(port, logger)
    await asyncio.sleep(1)

    # start prep procedure
    result = await pam4_preset_framelock(
        logger,
        port,
        should_link_recovery,
        should_an,
        preset,
        serdes,
        an_good_check_retries,
        frame_lock_retries,
        should_pam4pre
    )

    # stop anlt on the port
    logger.info(f"Stopping ANLT on Xena Port {port.kind.module_id}/{port.kind.port_id}")
    await anlt.anlt_stop(port)

    # free the port
    await mgmt.free_port(port)

    # print and return result
    if result:
        logger.info(f"Preset Frame Lock Test (OK)")
    else:
        logger.info(f"Preset Frame Lock Test (FAILED)")
    return result


async def preset_performance(
    chassis_ip: str,
    module_id: int,
    port_id: int,
    username: str,
    should_link_recovery: bool,
    should_an: bool,
    preset: int,
    serdes: int,
    logger: logging.Logger,
    an_good_check_retries: int,
    frame_lock_retries: int,
    should_pam4pre: bool
) -> bool:

    # connect to chassis, reserve and reset the Xena port
    port = await connect_reserver_reset(chassis_ip, module_id, port_id, username, logger)
    if not isinstance(port, ports.Z800FreyaPort):
        logger.info(f"Non-Freya port is used. Aborted")
        return False
    
    # reset Xena port TX taps to have a clean start
    await reset_freya_port_tx_tap(port, logger)
    await asyncio.sleep(1)

    # start prep procedure
    if not await pam4_preset_framelock(
        logger,
        port,
        should_link_recovery,
        should_an,
        preset,
        serdes,
        an_good_check_retries,
        frame_lock_retries,
        should_pam4pre
    ):
        logger.info(f"Preset Performance Test (FAILED)")
        return False
    
    # measure LT BER
    resp = await anlt.lt_status(port=port, serdes=serdes)
    _lt_ber = resp['ber']
    logger.info(f"Total bits        : {resp['total_bits']:,}")
    logger.info(f"Total err. bits   : {resp['total_errored_bits']:,}")
    logger.info(f"BER               : {resp['ber']}")

    # stop anlt on the port because we will move to DATA Phase
    logger.info(f"Stopping ANLT on Xena Port {port.kind.module_id}/{port.kind.port_id}")
    await anlt.anlt_stop(port)

    await asyncio.sleep(1)

    # free the port
    await mgmt.free_port(port)

    logger.info(f"Preset Performance Test (OK)")
    return True


async def coeff_boundary_max_min_limit_test(
    logger: logging.Logger,
    chassis_ip: str,
    module_id: int,
    port_id: int,
    username: str,
    should_link_recovery: bool,
    should_an: bool,
    preset: int,
    coeff: enums.LinkTrainCoeffs,
    type: str,  # allowed values: "max", "min"
    serdes: int,
    an_good_check_retries: int,
    frame_lock_retries: int,
    should_pam4pre: bool
) -> bool:

    type = type.lower()
    # connect to chassis, reserve and reset the Xena port
    port = await connect_reserver_reset(chassis_ip, module_id, port_id, username, logger)
    if not isinstance(port, ports.Z800FreyaPort):
        logger.info(f"Non-Freya port is used. Aborted")
        return False
    
    # reset Xena port TX taps to have a clean start
    await reset_freya_port_tx_tap(port, logger)
    await asyncio.sleep(1)

    # start prep procedure
    if not await pam4_preset_framelock(
        logger,
        port,
        should_link_recovery,
        should_an,
        preset,
        serdes,
        an_good_check_retries,
        frame_lock_retries,
        should_pam4pre
    ):
        logger.info(f"Coefficient {'Maximum' if type=='max' else 'Minimum'} Limit Test (FAILED)")
        return False

    # Request the remote port to inc/dec their tap until limit reached or timeout
    help_dict = {
        "pre3": enums.LinkTrainCoeffs.MAIN,
        "pre2": enums.LinkTrainCoeffs.MAIN,
        "pre": enums.LinkTrainCoeffs.MAIN,
        "main": enums.LinkTrainCoeffs.PRE,
        "post": enums.LinkTrainCoeffs.MAIN,
    }
    if type == "max":
        func = anlt.lt_coeff_inc
        cunf = anlt.lt_coeff_dec
    else:
        func = anlt.lt_coeff_dec
        cunf = anlt.lt_coeff_inc

    logger.info(f"Requesting the remote port to increase {coeff.name.upper()} on serdes {serdes} until coeff limit reached or timeout")
    await asyncio.sleep(1)

    # start the algorithm loop
    result = False
    not_updated_count = 0
    for _ in range(100):
        # request the remote port to inc/dec a coeff
        if type == "max":
            logger.warning(f"Request inc on {coeff.name.upper()}")
        else:
            logger.warning(f"Request dec on {coeff.name.upper()}")
        resp = await func(port, serdes, coeff)
        # if the response is COEFF_STS_AT_LIMIT or COEFF_STS_NOT_SUPPORTED, test is OK
        if resp in (
            enums.LinkTrainCmdResults.COEFF_STS_AT_LIMIT,
            enums.LinkTrainCmdResults.COEFF_STS_NOT_SUPPORTED,
            ):
            logger.info(f"Response: {resp.name}")
            logger.info(f"OK")
            logger.info(f"----")
            result = True
            break
        # if the response is TIMEOUT, test is failed
        elif resp in (
            enums.LinkTrainCmdResults.TIMEOUT,
            enums.LinkTrainCmdResults.UNKNOWN,
            enums.LinkTrainCmdResults.FAILED,
            ):
            logger.warning(f"Response: {resp.name}")
            logger.warning(f"----")
            result = False
            break
        # if the response is COEFF_STS_EQ_LIMIT or COEFF_STS_C_AND_EQ_LIMIT
        elif resp in (
            enums.LinkTrainCmdResults.COEFF_STS_EQ_LIMIT,
            enums.LinkTrainCmdResults.COEFF_STS_C_AND_EQ_LIMIT,
            ):
            logger.warning(f"Response: {resp.name}")
            logger.warning(f"----")
            result = False
            break
            
            # reverse the previous action
            # if type == "max":
            #     logger.warning(f"Request dec on {coeff.name.upper()} (reverse prev action)")
            # else:
            #     logger.warning(f"Request inc on {coeff.name.upper()} (reverse prev action)")
            # resp = await cunf(port, serdes, coeff)
            # logger.warning(f"Response: {resp.name}")

            # # request the remote port to give room
            # if type == "max":
            #     logger.info(f"!! Request the remote port to dec {help_dict[coeff.name.lower()].name.upper()} to give room for {coeff.name.upper()}")
            # else:
            #     logger.info(f"!! Request the remote port to inc {help_dict[coeff.name.lower()].name.upper()} to give room for {coeff.name.upper()}")
            # resp = await cunf(port, serdes, help_dict[coeff.name.lower()])
            # logger.warning(f"Response: {resp.name}")
            # if resp == enums.LinkTrainCmdResults.TIMEOUT:
            #     logger.warning(f"Response: {resp.name}")
            #     logger.warning(f"Failed due to TIMEOUT")
            #     logger.warning(f"----")
            #     result = False
            #     break
        elif resp in (
            enums.LinkTrainCmdResults.COEFF_STS_NOT_UPDATED,
            ):
            not_updated_count += 1
            if not_updated_count > 50:
                result = False
                break
            else:
                pass
        else:
            not_updated_count = 0
            logger.warning(f"Response: {resp.name}")
            pass

    logger.info(f"Stopping ANLT on Xena Port {port.kind.module_id}/{port.kind.port_id}")
    await anlt.anlt_stop(port)

    # free the port
    await mgmt.free_port(port)

    if result:
        logger.info(f"Coefficient {'Maximum' if type=='max' else 'Minimum'} Limit Test (OK)")
    else:
        logger.info(f"Coefficient {'Maximum' if type=='max' else 'Minimum'} Limit Test (FAILED)")
    return result


async def coeff_boundary_coeff_eq_limit_test(
    chassis_ip: str,
    module_id: int,
    port_id: int,
    username: str,
    should_link_recovery: bool,
    should_an: bool,
    preset: int,
    coeff: enums.LinkTrainCoeffs,
    serdes: int,
    logger: logging.Logger,
    an_good_check_retries: int,
    frame_lock_retries: int,
    should_pam4pre: bool
) -> bool:

    # connect to chassis, reserve and reset the Xena port
    port = await connect_reserver_reset(chassis_ip, module_id, port_id, username, logger)
    if not isinstance(port, ports.Z800FreyaPort):
        logger.info(f"Non-Freya port is used. Aborted")
        return False
    
    # reset Xena port TX taps to have a clean start
    await reset_freya_port_tx_tap(port, logger)

    # start prep procedure
    if not await pam4_preset_framelock(
        logger,
        port,
        should_link_recovery,
        should_an,
        preset,
        serdes,
        an_good_check_retries,
        frame_lock_retries,
        should_pam4pre
    ):
        logger.info(f"Coefficient & EQ Limit Test (FAILED)")
        return False

    # Request the remote port to inc their tap until limit reached or timeout
    logger.info(f"Requesting the remote port to increase {coeff.name.upper()} on serdes {serdes} until COEFF and/or EQ limit reached or timeout")
    await asyncio.sleep(1)
    
    # start the algorithm loop
    result = False
    not_updated_count = 0
    for _ in range(100):
        # request the remote port to increase coeff
        resp = await anlt.lt_coeff_inc(port, serdes, coeff)
        # if response is COEFF_STS_EQ_LIMIT or COEFF_STS_C_AND_EQ_LIMIT or COEFF_STS_AT_LIMIT or COEFF_STS_NOT_SUPPORTED
        if resp in (
            enums.LinkTrainCmdResults.COEFF_STS_EQ_LIMIT,
            enums.LinkTrainCmdResults.COEFF_STS_C_AND_EQ_LIMIT,
            enums.LinkTrainCmdResults.COEFF_STS_AT_LIMIT,
            enums.LinkTrainCmdResults.COEFF_STS_NOT_SUPPORTED,
        ):
            logger.info(f"Response: {resp.name}")
            logger.info(f"OK")
            logger.info(f"----")
            result = True
            break
        # if the response is TIMEOUT, test is failed
        elif resp in (
            enums.LinkTrainCmdResults.TIMEOUT,
            enums.LinkTrainCmdResults.UNKNOWN,
            enums.LinkTrainCmdResults.FAILED,
        ):
            logger.warning(f"Response: {resp.name}")
            logger.warning(f"Failed due to TIMEOUT")
            logger.warning(f"----")
            result = False
            break
        elif resp in (
            enums.LinkTrainCmdResults.COEFF_STS_NOT_UPDATED,
            ):
            not_updated_count += 1
            if not_updated_count > 50:
                result = False
                break
            else:
                pass
        else:
            not_updated_count = 0
            logger.warning(f"Response: {resp.name}")
            pass
    
    logger.info(f"Stopping ANLT on Xena Port {port.kind.module_id}/{port.kind.port_id}")
    resp = await anlt.lt_trained(port, serdes)
    await anlt.anlt_stop(port)

    # free the port
    await mgmt.free_port(port)

    if result:
        logger.info(f"Coefficient EQ Limit Test (OK)")
    else:
        logger.info(f"Coefficient EQ Limit Test (FAILED)")
    return result


#endregion